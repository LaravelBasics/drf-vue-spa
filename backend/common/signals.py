"""
監査ログ用シグナル（全モデル自動監視）

改善点:
- ループ内デコレーター問題を修正
- クロージャを正しく使用
- メモリリーク対策
"""

import logging
import json
from django.apps import apps
from django.db.models.signals import post_save, post_delete, pre_save
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
    """
    監査対象かチェック

    Args:
        model: Djangoモデルクラス

    Returns:
        bool: 監査対象ならTrue
    """
    model_label = f"{model._meta.app_label}.{model._meta.model_name}"
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


def create_pre_save_handler():
    """
    pre_saveハンドラーを生成

    更新前の値を保存するハンドラーを返す

    Returns:
        function: シグナルハンドラー
    """

    def handler(sender, instance, **kwargs):
        """更新前の値をインスタンスに保存"""
        if instance.pk:
            try:
                old = sender.objects.get(pk=instance.pk)
                instance._old_instance = old
            except sender.DoesNotExist:
                pass

    return handler


def create_post_save_handler():
    """
    post_saveハンドラーを生成

    作成・更新を記録するハンドラーを返す

    Returns:
        function: シグナルハンドラー
    """

    def handler(sender, instance, created, **kwargs):
        """作成・更新を監査ログに記録"""
        action = "CREATE" if created else "UPDATE"
        changes = {}

        if not created and hasattr(instance, "_old_instance"):
            changes = get_field_changes(instance._old_instance, instance)

        log_audit(action, instance, changes)

    return handler


def create_post_delete_handler():
    """
    post_deleteハンドラーを生成

    削除を記録するハンドラーを返す

    Returns:
        function: シグナルハンドラー
    """

    def handler(sender, instance, **kwargs):
        """削除を監査ログに記録"""
        log_audit("DELETE", instance)

    return handler


def register_audit_signals():
    """
    全モデルにシグナルを登録

    監査対象のすべてのモデルに対して、
    作成・更新・削除を記録するシグナルを登録する

    Note:
        - EXCLUDE_MODELS に登録されたモデルは除外される
        - 各モデルごとに専用のハンドラーインスタンスを作成
        - weak=False で確実に登録される
    """
    for model in apps.get_models():
        if not should_audit(model):
            continue

        # 各モデルごとに専用のハンドラーを作成して登録
        pre_save.connect(
            create_pre_save_handler(),
            sender=model,
            weak=False,
            dispatch_uid=f"audit_pre_save_{model._meta.label}",
        )

        post_save.connect(
            create_post_save_handler(),
            sender=model,
            weak=False,
            dispatch_uid=f"audit_post_save_{model._meta.label}",
        )

        post_delete.connect(
            create_post_delete_handler(),
            sender=model,
            weak=False,
            dispatch_uid=f"audit_post_delete_{model._meta.label}",
        )
