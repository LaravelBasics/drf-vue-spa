# backend/users/services/user_service.py
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError
from audit.utils import create_audit_log, get_model_changes

User = get_user_model()


class UserService:
    """ユーザー管理のビジネスロジック（論理削除・高速化対応）"""

    @staticmethod
    def _check_last_admin(user_id=None, is_admin=None, is_active=None):
        """
        管理者が最低1人残るかチェック（高速化版）
        
        Args:
            user_id: 対象ユーザーID（更新・削除時）
            is_admin: 管理者フラグ（更新時）
            is_active: 有効フラグ（更新時）
        
        Raises:
            ValidationError: 最後の管理者を削除・無効化しようとした場合
        """
        query = User.objects.filter(is_admin=True, is_active=True)
        
        if user_id:
            query = query.exclude(id=user_id)
        
        if not query.exists():
            if is_admin is None and is_active is None:
                raise ValidationError(
                    "管理者は最低1人必要です。最後の管理者を削除することはできません。"
                )
            elif is_admin is False or is_active is False:
                raise ValidationError(
                    "管理者は最低1人必要です。最後の管理者の権限を削除することはできません。"
                )

    @staticmethod
    @transaction.atomic
    def create_user(validated_data):
        """
        ユーザー作成
        
        Args:
            validated_data: シリアライザーで検証済みのデータ
        
        Returns:
            User: 作成されたユーザーインスタンス
        """
        password = validated_data.pop('password', None)
        
        # CustomUserManager.create_user() を使用してパスワードを自動ハッシュ化
        user = User.objects.create_user(
            password=password or 'defaultpassword123',
            **validated_data
        )
        
        return user

    @staticmethod
    @transaction.atomic
    def update_user(user_instance, validated_data):
        """ユーザー更新（監査ログ対応）"""
        """
        ユーザー更新（高速化版）
        
        Args:
            user_instance: 更新対象のUserインスタンス
            validated_data: シリアライザーで検証済みのデータ
        
        Returns:
            User: 更新されたユーザーインスタンス
        
        Raises:
            ValidationError: 最後の管理者を無効化しようとした場合
        """

        # 変更内容を記録
        changes = get_model_changes(user_instance, validated_data)
        # 管理者チェック（更新前の状態と更新後の状態を比較）
        if user_instance.is_admin:
            new_is_admin = validated_data.get('is_admin', user_instance.is_admin)
            new_is_active = validated_data.get('is_active', user_instance.is_active)
            
            UserService._check_last_admin(
                user_id=user_instance.id,
                is_admin=new_is_admin,
                is_active=new_is_active
            )
        
        # パスワード処理を分離
        password = validated_data.pop('password', None)
        
        # 通常のフィールド更新
        update_fields = []
        for attr, value in validated_data.items():
            setattr(user_instance, attr, value)
            update_fields.append(attr)
        
        # パスワードが指定されている場合はハッシュ化して保存
        if password:
            user_instance.set_password(password)
            update_fields.append('password')
        
        if update_fields:
            user_instance.save(update_fields=update_fields)
        
        # ⭐ 監査ログを記録
        create_audit_log(
            action='UPDATE',
            model_name='User',
            object_id=user_instance.id,
            changes=changes
        )

        return user_instance

    @staticmethod
    @transaction.atomic
    def delete_user(user_instance):
        """
        ユーザー削除（論理削除）
        
        Args:
            user_instance: 削除対象のUserインスタンス
        
        Raises:
            ValidationError: 最後の管理者を削除しようとした場合
        """
        # 管理者チェック
        if user_instance.is_admin:
            UserService._check_last_admin(user_id=user_instance.id)
        
        # 論理削除
        user_instance.soft_delete()

        # ⭐ 監査ログを記録
        create_audit_log(
            action='DELETE',
            model_name='User',
            object_id=user_instance.id
        )
    
    @staticmethod
    @transaction.atomic
    def bulk_delete_users(user_ids):
        """
        一括論理削除（高速化版）
        
        Args:
            user_ids: 削除対象のユーザーIDリスト
        
        Returns:
            int: 削除したユーザー数
        
        Raises:
            ValidationError: 管理者が削除対象に含まれている場合
        """
        from django.utils import timezone
        
        # 削除対象に管理者が含まれているかチェック
        admin_ids = list(
            User.objects.filter(
                id__in=user_ids,
                is_admin=True,
                is_active=True
            ).values_list('id', flat=True)
        )
        
        if admin_ids:
            # 削除後に管理者が0人になるかチェック
            remaining_admins = User.objects.filter(
                is_admin=True,
                is_active=True
            ).exclude(id__in=user_ids).exists()
            
            if not remaining_admins:
                raise ValidationError(
                    "管理者は最低1人必要です。すべての管理者を削除することはできません。"
                )
        
        # 一括論理削除
        updated_count = User.objects.filter(id__in=user_ids).update(
            deleted_at=timezone.now(),
            is_active=False
        )
        
        return updated_count
    
    @staticmethod
    def restore_user(user_id):
        """
        ユーザー復元
        
        Args:
            user_id: 復元対象のユーザーID
        
        Returns:
            User: 復元されたユーザーインスタンス
        
        Raises:
            User.DoesNotExist: ユーザーが存在しない場合
        """
        # 削除済みユーザーを取得（all_objects使用）
        user = User.all_objects.get(id=user_id, deleted_at__isnull=False)
        user.restore()
        return user
    
    @staticmethod
    @transaction.atomic
    def bulk_restore_users(user_ids):
        """
        一括復元
        
        Args:
            user_ids: 復元対象のユーザーIDリスト
        
        Returns:
            int: 復元したユーザー数
        """
        updated_count = User.all_objects.filter(
            id__in=user_ids,
            deleted_at__isnull=False
        ).update(
            deleted_at=None,
            is_active=True
        )
        
        return updated_count
    
    @staticmethod
    def permanent_delete_old_users(days=90):
        """
        古い削除済みユーザーを物理削除（定期実行用）
        
        Args:
            days: 何日前に削除されたユーザーを対象とするか
        
        Returns:
            int: 物理削除したユーザー数
        """
        from django.utils import timezone
        from datetime import timedelta
        
        threshold_date = timezone.now() - timedelta(days=days)
        
        old_deleted_users = User.all_objects.filter(
            deleted_at__lte=threshold_date
        )
        
        count = old_deleted_users.count()
        old_deleted_users.delete()  # 物理削除
        
        return count