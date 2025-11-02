"""
ユーザー管理ビジネスロジック
"""

from django.contrib.auth import get_user_model
from django.db import transaction
from ..exceptions import LastAdminError, CannotDeleteSelfError

User = get_user_model()


class UserService:
    """ユーザー管理サービス"""

    @staticmethod
    def _get_active_admin_count(exclude_user_id=None):
        """
        アクティブな管理者数を取得

        Args:
            exclude_user_id: カウントから除外するユーザーID

        Returns:
            int: 管理者数
        """
        query = User.objects.filter(is_admin=True, is_active=True)

        if exclude_user_id:
            query = query.exclude(id=exclude_user_id)

        return query.count()

    @staticmethod
    def _check_last_admin_for_delete(user_id):
        """
        削除時の最後の管理者チェック

        Raises:
            LastAdminError: 管理者が0人になる場合
        """
        if UserService._get_active_admin_count(exclude_user_id=user_id) == 0:
            raise LastAdminError(action="delete")

    @staticmethod
    def _check_last_admin_for_update(user_id, new_is_admin, new_is_active):
        """
        更新時の最後の管理者チェック

        Args:
            user_id: 更新対象ユーザーID
            new_is_admin: 更新後の管理者フラグ
            new_is_active: 更新後のアクティブフラグ

        Raises:
            LastAdminError: 管理者が0人になる場合
        """
        if UserService._get_active_admin_count(exclude_user_id=user_id) == 0:
            # 管理者権限を剥奪する場合
            if new_is_admin is False:
                raise LastAdminError(action="demote")

            # 無効化する場合
            if new_is_active is False:
                raise LastAdminError(action="deactivate")

    @staticmethod
    @transaction.atomic
    def create_user(validated_data):
        """
        ユーザー作成

        Args:
            validated_data: バリデーション済みデータ

        Returns:
            作成されたユーザー
        """
        password = validated_data.pop("password", None)

        user = User.objects.create_user(
            password=password or "defaultpassword123", **validated_data
        )

        return user

    @staticmethod
    @transaction.atomic
    def update_user(user_instance, validated_data):
        """
        ユーザー更新

        Args:
            user_instance: 更新対象ユーザー
            validated_data: 更新データ

        Returns:
            更新されたユーザー
        """
        if user_instance.is_admin:
            new_is_admin = validated_data.get("is_admin", user_instance.is_admin)
            new_is_active = validated_data.get("is_active", user_instance.is_active)

            UserService._check_last_admin_for_update(
                user_id=user_instance.id,
                new_is_admin=new_is_admin,
                new_is_active=new_is_active,
            )

        password = validated_data.pop("password", None)

        update_fields = []
        for attr, value in validated_data.items():
            setattr(user_instance, attr, value)
            update_fields.append(attr)

        if password:
            user_instance.set_password(password)
            update_fields.append("password")

        if update_fields:
            update_fields.append("updated_at")
            user_instance.save(update_fields=update_fields)

        return user_instance

    @staticmethod
    def delete_user(user_instance, request_user_id=None):
        """
        ユーザー削除（論理削除）

        Args:
            user_instance: 削除対象ユーザー
            request_user_id: 削除実行ユーザーID
        """
        if request_user_id and user_instance.id == request_user_id:
            raise CannotDeleteSelfError()

        if user_instance.is_admin:
            UserService._check_last_admin_for_delete(user_id=user_instance.id)

        user_instance.soft_delete()
