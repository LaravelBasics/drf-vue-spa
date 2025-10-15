# backend/users/services/user_service.py
"""
ユーザー管理のビジネスロジック

このファイルの役割:
- ユーザーの作成・更新・削除などの「業務ルール」を管理
- データベース操作を1つにまとめる（トランザクション管理）
- 「最後の管理者を削除させない」などのチェック

なぜ service.py が必要？:
- views.py に全部書くと複雑になる
- 同じ処理を複数の場所で使える
- テストしやすい
"""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from ..exceptions import LastAdminError, UserNotFoundError, CannotDeleteSelfError

User = get_user_model()


class UserService:
    """ユーザー管理の業務ルールをまとめたクラス"""

    # ==================== 内部チェック関数 ====================
    
    @staticmethod
    def _check_last_admin(user_id=None, is_admin=None, is_active=None):
        """
        最後の管理者を削除・無効化しようとしていないかチェック
        
        業務ルール:
        - システムには必ず1人以上の管理者が必要
        - 最後の1人を削除・無効化してはいけない
        
        引数:
            user_id: チェック対象のユーザーID（このユーザーを除外して数える）
            is_admin: 管理者権限を外そうとしている場合 False
            is_active: アカウントを無効化しようとしている場合 False
        
        エラー:
            LastAdminError: 最後の管理者を削除しようとした場合
        """
        # 現在アクティブな管理者を検索
        query = User.objects.filter(is_admin=True, is_active=True)
        
        # 対象ユーザーを除外（削除・更新する場合）
        if user_id:
            query = query.exclude(id=user_id)
        
        # 管理者が0人になるかチェック
        if not query.exists():
            # エラーメッセージを状況に応じて変更
            action = '削除'
            if is_admin is False:
                action = '管理者権限から外す'
            elif is_active is False:
                action = '無効化'
            
            raise LastAdminError(action=action)

    # ==================== CRUD操作 ====================
    
    @staticmethod
    @transaction.atomic  # データベース操作を1つの処理としてまとめる
    def create_user(validated_data):
        """
        ユーザーを作成する
        
        引数:
            validated_data: シリアライザーでチェック済みのデータ
                例: {
                    'employee_id': 'EMP001',
                    'username': '山田太郎',
                    'password': 'password123',
                    'is_admin': False
                }
        
        戻り値:
            作成されたユーザー
        """
        # パスワードだけ別処理（ハッシュ化が必要）
        password = validated_data.pop('password', None)
        
        # ユーザー作成（models.py の create_user メソッドを使用）
        user = User.objects.create_user(
            password=password or 'defaultpassword123',  # パスワードがない場合のデフォルト
            **validated_data  # その他のフィールド
        )
        
        return user

    @staticmethod
    @transaction.atomic
    def update_user(user_instance, validated_data):
        """
        ユーザー情報を更新する
        
        引数:
            user_instance: 更新対象のユーザー
            validated_data: 更新するデータ
        
        戻り値:
            更新されたユーザー
        
        チェック内容:
        - 最後の管理者を無効化しようとしていないか
        - 最後の管理者から管理者権限を外そうとしていないか
        """
        
        # 管理者の場合、最後の1人でないかチェック
        if user_instance.is_admin:
            # 更新後の値を取得（変更がない場合は現在の値）
            new_is_admin = validated_data.get('is_admin', user_instance.is_admin)
            new_is_active = validated_data.get('is_active', user_instance.is_active)
            
            # 最後の管理者チェック
            UserService._check_last_admin(
                user_id=user_instance.id,
                is_admin=new_is_admin,
                is_active=new_is_active
            )
        
        # パスワードは別処理（ハッシュ化が必要）
        password = validated_data.pop('password', None)
        
        # 通常のフィールドを更新
        update_fields = []
        for attr, value in validated_data.items():
            setattr(user_instance, attr, value)  # user.username = '新しい名前' のような処理
            update_fields.append(attr)
        
        # パスワードが指定されていれば更新
        if password:
            user_instance.set_password(password)  # ハッシュ化して保存
            update_fields.append('password')
        
        # データベースに保存（変更されたフィールドのみ）
        if update_fields:
            user_instance.save(update_fields=update_fields)

        return user_instance

    @staticmethod
    @transaction.atomic
    def delete_user(user_instance, request_user_id=None):
        """
        ユーザーを削除する（論理削除）
        
        論理削除とは:
        - データベースから完全に消すのではなく
        - deleted_at に日時を記録して「削除済み」とマークする
        - 後で復元できる
        
        引数:
            user_instance: 削除対象のユーザー
            request_user_id: 削除を実行しているユーザーのID
        
        エラー:
            CannotDeleteSelfError: 自分自身を削除しようとした
            LastAdminError: 最後の管理者を削除しようとした
        """
        # 自分自身を削除しようとしていないかチェック
        if request_user_id and user_instance.id == request_user_id:
            raise CannotDeleteSelfError()
        
        # 管理者の場合、最後の1人でないかチェック
        if user_instance.is_admin:
            UserService._check_last_admin(user_id=user_instance.id)
        
        # 論理削除を実行（models.py の soft_delete メソッド）
        user_instance.soft_delete()

    # ==================== 一括操作 ====================

    @staticmethod
    @transaction.atomic
    def bulk_delete_users(user_ids):
        """
        複数のユーザーを一括で論理削除
        
        引数:
            user_ids: 削除するユーザーIDのリスト
                例: [1, 2, 3]
        
        戻り値:
            削除した件数
        
        チェック内容:
        - 削除対象に管理者が含まれる場合
        - 削除後も最低1人の管理者が残るか確認
        """
        
        # 削除対象に含まれる管理者のIDを取得
        admin_ids = list(
            User.objects.filter(
                id__in=user_ids,
                is_admin=True,
                is_active=True
            ).values_list('id', flat=True)
        )
        
        # 管理者が含まれる場合
        if admin_ids:
            # 削除後も管理者が残るかチェック
            remaining_admins = User.objects.filter(
                is_admin=True,
                is_active=True
            ).exclude(id__in=user_ids).exists()
            
            # 管理者が0人になる場合はエラー
            if not remaining_admins:
                raise LastAdminError(action='削除')
        
        # 一括で論理削除（deleted_at と is_active を更新）
        updated_count = User.objects.filter(id__in=user_ids).update(
            deleted_at=timezone.now(),
            is_active=False
        )
        
        return updated_count
    
    # ==================== 復元処理 ====================
    
    @staticmethod
    @transaction.atomic
    def restore_user(user_id):
        """
        削除済みユーザーを復元する
        
        引数:
            user_id: 復元するユーザーのID
        
        戻り値:
            復元されたユーザー
        
        エラー:
            UserNotFoundError: ユーザーが見つからない
        """
        try:
            # 削除済みユーザーを検索（all_objects で削除済みも含む）
            user = User.all_objects.get(id=user_id, deleted_at__isnull=False)
        except User.DoesNotExist:
            raise UserNotFoundError()
        
        # 復元処理（models.py の restore メソッド）
        user.restore()
        return user
    
    @staticmethod
    @transaction.atomic
    def bulk_restore_users(user_ids):
        """
        複数のユーザーを一括で復元
        
        引数:
            user_ids: 復元するユーザーIDのリスト
        
        戻り値:
            復元した件数
        """
        updated_count = User.all_objects.filter(
            id__in=user_ids,
            deleted_at__isnull=False
        ).update(
            deleted_at=None,
            is_active=True
        )
        
        return updated_count
    
    # ==================== メンテナンス処理 ====================
    
    @staticmethod
    @transaction.atomic
    def permanent_delete_old_users(days=90):
        """
        古い削除済みユーザーを完全に削除（物理削除）
        
        物理削除とは:
        - データベースから完全に消す（復元不可）
        - 定期的に実行してデータベースを掃除する
        
        引数:
            days: 削除後何日経過したユーザーを対象とするか（デフォルト: 90日）
        
        戻り値:
            物理削除した件数
        
        使い方:
        python manage.py cleanup_deleted_users --days=90
        """
        
        # 基準日を計算（今日から90日前）
        threshold_date = timezone.now() - timedelta(days=days)
        
        # 基準日より前に削除されたユーザーを検索
        old_deleted_users = User.all_objects.filter(
            deleted_at__lte=threshold_date
        )
        
        # 件数を記録してから削除
        count = old_deleted_users.count()
        old_deleted_users.delete()  # 物理削除
        
        return count