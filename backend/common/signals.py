"""
監査ログ用シグナル（全モデル自動監視）
"""

import logging
import json
from django.apps import apps
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from common.context import get_current_request, get_client_ip

audit_logger = logging.getLogger("audit")

# 監査対象外のモデル
EXCLUDE_MODELS = [
    "contenttypes.contenttype",
    "sessions.session",
    "admin.logentry",
]

# 機密フィールド
SENSITIVE_FIELDS = ["password", "token", "secret_key", "api_key"]


def should_audit(model):
    """監査対象かチェック"""
    model_label = f"{model._meta.app_label}.{model._meta.model_name}"
    return model_label not in EXCLUDE_MODELS


def get_field_changes(old_instance, new_instance):
    """変更内容を抽出"""
    changes = {}

    for field in new_instance._meta.fields:
        field_name = field.name

        # 機密フィールドはマスク
        if field_name in SENSITIVE_FIELDS:
            old_value = getattr(old_instance, field_name)
            new_value = getattr(new_instance, field_name)
            if old_value != new_value:
                changes[field_name] = {"old": "***", "new": "***"}
            continue

        # 通常フィールド
        old_value = getattr(old_instance, field_name)
        new_value = getattr(new_instance, field_name)

        if old_value != new_value:
            changes[field_name] = {"old": str(old_value), "new": str(new_value)}

    return changes


def log_audit(action, instance, changes=None):
    """監査ログ出力"""
    request = get_current_request()

    user_info = "system"
    ip = "127.0.0.1"
    request_id = "N/A"

    if request:
        if hasattr(request, "user") and request.user.is_authenticated:
            user_info = getattr(request.user, "employee_id", request.user.username)
        ip = get_client_ip(request)
        request_id = getattr(request, "_request_id", "N/A")  # ⭐ リクエストID

    audit_logger.info(
        f"{instance._meta.model_name} {action}: {instance.pk}",
        extra={
            "request_id": request_id,  # ⭐ 追加
            "user": user_info,
            "action": action,
            "model": instance._meta.model_name.capitalize(),
            "object_id": instance.pk,
            "ip": ip,
            "changes": json.dumps(changes or {}, ensure_ascii=False),
        },
    )


def register_audit_signals():
    """全モデルにシグナルを登録"""

    for model in apps.get_models():
        if not should_audit(model):
            continue

        # pre_save: 更新前の値を保存
        @receiver(pre_save, sender=model, weak=False)
        def model_pre_save(sender, instance, **kwargs):
            if instance.pk:
                try:
                    old = sender.objects.get(pk=instance.pk)
                    instance._old_instance = old
                except sender.DoesNotExist:
                    pass

        # post_save: 作成/更新を記録
        @receiver(post_save, sender=model, weak=False)
        def model_post_save(sender, instance, created, **kwargs):
            action = "CREATE" if created else "UPDATE"
            changes = {}

            if not created and hasattr(instance, "_old_instance"):
                changes = get_field_changes(instance._old_instance, instance)

            log_audit(action, instance, changes)

        # post_delete: 削除を記録
        @receiver(post_delete, sender=model, weak=False)
        def model_post_delete(sender, instance, **kwargs):
            log_audit("DELETE", instance)
