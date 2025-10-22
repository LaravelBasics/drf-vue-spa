"""
監査ログ用シグナル（Userモデルのみ）
"""

import logging
import json
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from common.context import get_current_request, get_client_ip

User = get_user_model()
audit_logger = logging.getLogger("audit")

# 機密フィールド（ログに残さない）
SENSITIVE_FIELDS = ["password"]


@receiver(pre_save, sender=User)
def user_pre_save(sender, instance, **kwargs):
    """ユーザー更新前（変更内容を記録）"""
    if instance.pk:
        try:
            old = User.all_objects.get(pk=instance.pk)
            instance._old_values = {
                "username": old.username,
                "employee_id": old.employee_id,
                "is_admin": old.is_admin,
                "is_active": old.is_active,
            }
        except User.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """ユーザー作成・更新後"""
    action = "CREATE" if created else "UPDATE"

    # 変更内容を抽出
    changes = {}
    if not created and hasattr(instance, "_old_values"):
        old = instance._old_values
        for field, old_value in old.items():
            new_value = getattr(instance, field)
            if old_value != new_value:
                # 機密フィールドはマスク
                if field in SENSITIVE_FIELDS:
                    changes[field] = {"old": "***", "new": "***"}
                else:
                    changes[field] = {"old": old_value, "new": new_value}

    # リクエスト情報
    request = get_current_request()
    user_info = "system"
    ip = "127.0.0.1"

    if request and hasattr(request, "user") and request.user.is_authenticated:
        user_info = request.user.employee_id
        ip = get_client_ip(request)

    # ログ記録
    audit_logger.info(
        f"User {action}: {instance.username}",
        extra={
            "user": user_info,
            "action": action,
            "model": "User",
            "object_id": instance.id,
            "ip": ip,
            "changes": json.dumps(changes, ensure_ascii=False),
        },
    )


@receiver(post_delete, sender=User)
def user_post_delete(sender, instance, **kwargs):
    """ユーザー削除後"""
    request = get_current_request()
    user_info = "system"
    ip = "127.0.0.1"

    if request and hasattr(request, "user") and request.user.is_authenticated:
        user_info = request.user.employee_id
        ip = get_client_ip(request)

    audit_logger.info(
        f"User DELETE: {instance.username}",
        extra={
            "user": user_info,
            "action": "DELETE",
            "model": "User",
            "object_id": instance.id,
            "ip": ip,
            "changes": "{}",
        },
    )
