# backend/users/services/user_service.py

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from audit.utils import create_audit_log, get_model_changes
from ..exceptions import LastAdminError, UserNotFoundError, CannotDeleteSelfError, CannotUpdateDeletedError

User = get_user_model()


class UserService:
    """ユーザー管理のビジネスロジック（エラーコード対応版）"""

    @staticmethod
    def _check_last_admin(user_id=None, is_admin=None, is_active=None):
        """
        管理者が最低1人残るかチェック
        
        Raises:
            LastAdminError: 最後の管理者を削除・無効化しようとした場合
        """
        query = User.objects.filter(is_admin=True, is_active=True)
        
        if user_id:
            query = query.exclude(id=user_id)
        
        if not query.exists():
            action = '削除'
            if is_admin is False:
                action = '管理者権限から外す'
            elif is_active is False:
                action = '無効化'
            
            raise LastAdminError(action=action)

    @staticmethod
    @transaction.atomic
    def create_user(validated_data):
        """ユーザー作成"""
        password = validated_data.pop('password', None)
        
        user = User.objects.create_user(
            password=password or 'defaultpassword123',
            **validated_data
        )

        create_audit_log(
            action='CREATE',
            model_name='User',
            object_id=user.id,
            changes={
                'username': {'old': None, 'new': user.username},
                'employee_id': {'old': None, 'new': user.employee_id},
                'is_admin': {'old': None, 'new': user.is_admin},
                'password': {'old': None, 'new': '***'},
            }
        )
        
        return user

    @staticmethod
    @transaction.atomic
    def update_user(user_instance, validated_data):
        """ユーザー更新（service に全責任を委譲）"""
        
        changes = get_model_changes(user_instance, validated_data)
        
        # 最後の管理者チェック（views では判定しない）
        if user_instance.is_admin:
            new_is_admin = validated_data.get('is_admin', user_instance.is_admin)
            new_is_active = validated_data.get('is_active', user_instance.is_active)
            
            UserService._check_last_admin(
                user_id=user_instance.id,
                is_admin=new_is_admin,
                is_active=new_is_active
            )
        
        password = validated_data.pop('password', None)
        
        update_fields = []
        for attr, value in validated_data.items():
            setattr(user_instance, attr, value)
            update_fields.append(attr)
        
        if password:
            user_instance.set_password(password)
            update_fields.append('password')
        
        if update_fields:
            user_instance.save(update_fields=update_fields)
        
        create_audit_log(
            action='UPDATE',
            model_name='User',
            object_id=user_instance.id,
            changes=changes
        )

        return user_instance

    @staticmethod
    @transaction.atomic
    def delete_user(user_instance, request_user_id=None):
        """
        ユーザー削除（論理削除）
        
        Raises:
            CannotDeleteSelfError: 自分自身を削除しようとした場合
            LastAdminError: 最後の管理者を削除しようとした場合
        """
        if request_user_id and user_instance.id == request_user_id:
            raise CannotDeleteSelfError()
        
        if user_instance.is_admin:
            UserService._check_last_admin(user_id=user_instance.id)
        
        user_instance.soft_delete()

        create_audit_log(
            action='DELETE',
            model_name='User',
            object_id=user_instance.id
        )
    
    @staticmethod
    @transaction.atomic
    def bulk_delete_users(user_ids):
        """一括論理削除"""
        
        admin_ids = list(
            User.objects.filter(
                id__in=user_ids,
                is_admin=True,
                is_active=True
            ).values_list('id', flat=True)
        )
        
        if admin_ids:
            remaining_admins = User.objects.filter(
                is_admin=True,
                is_active=True
            ).exclude(id__in=user_ids).exists()
            
            if not remaining_admins:
                raise LastAdminError(action='削除')
        
        updated_count = User.objects.filter(id__in=user_ids).update(
            deleted_at=timezone.now(),
            is_active=False
        )
        
        return updated_count
    
    @staticmethod
    def restore_user(user_id):
        """ユーザー復元"""
        try:
            user = User.all_objects.get(id=user_id, deleted_at__isnull=False)
        except User.DoesNotExist:
            raise UserNotFoundError()
        
        user.restore()
        return user
    
    @staticmethod
    @transaction.atomic
    def bulk_restore_users(user_ids):
        """一括復元"""
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
        """古い削除済みユーザーを物理削除"""
        
        threshold_date = timezone.now() - timedelta(days=days)
        
        old_deleted_users = User.all_objects.filter(
            deleted_at__lte=threshold_date
        )
        
        count = old_deleted_users.count()
        old_deleted_users.delete()
        
        return count