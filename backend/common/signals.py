"""
監査ログ用シグナル(全モデル自動監視)

Django公式推奨の@receiverデコレーターパターンに準拠
Over-Engineeringを排除し、シンプルで保守性の高い実装
"""

import logging
import json
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from common.context import get_current_request, get_client_ip

audit_logger = logging.getLogger("audit")

# 監査対象外のモデル
EXCLUDE_MODELS = {
    "contenttypes.contenttype",
    "sessions.session",
    "admin.logentry",
}

# 機密フィールド
SENSITIVE_FIELDS = {"password", "token", "secret_key", "api_key"}


def should_audit(sender):
    """
    監査対象かチェック

    Args:
        sender: Djangoモデルクラス

    Returns:
        bool: 監査対象ならTrue
    """
    model_label = f"{sender._meta.app_label}.{sender._meta.model_name}"
    return model_label not in EXCLUDE_MODELS


def get_field_changes(old_instance, new_instance):
    """
    変更内容を抽出

    Args:
        old_instance: 更新前のインスタンス
        new_instance: 更新後のインスタンス

    Returns:
        dict: 変更内容 {field_name: {"old": value, "new": value}}
    """
    changes = {}

    for field in new_instance._meta.fields:
        field_name = field.name
        old_value = getattr(old_instance, field_name)
        new_value = getattr(new_instance, field_name)

        if old_value != new_value:
            # 機密フィールドはマスク
            if field_name in SENSITIVE_FIELDS:
                changes[field_name] = {"old": "***", "new": "***"}
            else:
                changes[field_name] = {"old": str(old_value), "new": str(new_value)}

    return changes


def log_audit(action, instance, changes=None):
    """
    監査ログ出力

    Args:
        action: アクション (CREATE/UPDATE/DELETE)
        instance: モデルインスタンス
        changes: 変更内容
    """
    request = get_current_request()

    user_info = "system"
    ip = "127.0.0.1"
    request_id = "N/A"

    if request:
        if hasattr(request, "user") and request.user.is_authenticated:
            user_info = getattr(request.user, "employee_id", request.user.username)
        ip = get_client_ip(request)
        request_id = getattr(request, "_request_id", "N/A")

    audit_logger.info(
        f"{instance._meta.model_name} {action}: {instance.pk}",
        extra={
            "request_id": request_id,
            "user": user_info,
            "action": action,
            "model": instance._meta.model_name.capitalize(),
            "object_id": instance.pk,
            "ip": ip,
            "changes": json.dumps(changes or {}, ensure_ascii=False),
        },
    )


@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    """
    更新前の値を保存

    Args:
        sender: モデルクラス
        instance: モデルインスタンス

    Note:
        @receiverデコレーターで全モデルに自動接続
    """
    if not should_audit(sender):
        return

    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._old_instance = old
        except sender.DoesNotExist:
            pass


@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    """
    作成・更新を監査ログに記録

    Args:
        sender: モデルクラス
        instance: モデルインスタンス
        created: 新規作成フラグ

    Note:
        @receiverデコレーターで全モデルに自動接続
    """
    if not should_audit(sender):
        return

    action = "CREATE" if created else "UPDATE"
    changes = {}

    if not created and hasattr(instance, "_old_instance"):
        changes = get_field_changes(instance._old_instance, instance)

    log_audit(action, instance, changes)


@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    """
    削除を監査ログに記録

    Args:
        sender: モデルクラス
        instance: モデルインスタンス

    Note:
        @receiverデコレーターで全モデルに自動接続
    """
    if not should_audit(sender):
        return

    log_audit("DELETE", instance)
