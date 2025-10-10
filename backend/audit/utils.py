# 3. backend/audit/utils.py
# ============================================
from .models import AuditLog
from .middleware import get_current_request, get_current_request_id
import json
import uuid


def get_client_ip(request):
    """クライアントIPアドレスを取得"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_audit_log(
    action,
    model_name,
    object_id=None,
    changes=None,
    success=True,
    error_message=None,
    request=None
):
    """
    監査ログを作成
    
    Args:
        action: アクション（CREATE, UPDATE, DELETE など）
        model_name: モデル名（User, Product など）
        object_id: オブジェクトID
        changes: 変更内容（辞書）
        success: 成功フラグ
        error_message: エラーメッセージ
        request: リクエストオブジェクト（省略時は自動取得）
    """
    if request is None:
        request = get_current_request()
    
    if not request:
        return None
    
    user = request.user if request.user.is_authenticated else None
    
    audit_log = AuditLog.objects.create(
        request_id=get_current_request_id() or str(uuid.uuid4()),
        user=user,
        employee_id=user.employee_id if user else None,
        username=user.username if user else None,
        action=action,
        model_name=model_name,
        object_id=str(object_id) if object_id else None,
        changes=changes,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        endpoint=request.path,
        method=request.method,
        success=success,
        error_message=error_message,
    )
    
    return audit_log


def get_model_changes(instance, validated_data):
    """
    モデルの変更内容を取得
    
    Args:
        instance: 更新前のインスタンス
        validated_data: 更新データ
    
    Returns:
        dict: {'field': {'old': 'value1', 'new': 'value2'}}
    """
    changes = {}
    
    for field, new_value in validated_data.items():
        if field == 'password':
            # パスワードは記録しない
            changes[field] = {'old': '***', 'new': '***'}
            continue
        
        old_value = getattr(instance, field, None)
        
        # 値が変更されている場合のみ記録
        if old_value != new_value:
            changes[field] = {
                'old': str(old_value) if old_value is not None else None,
                'new': str(new_value) if new_value is not None else None,
            }
    
    return changes if changes else None