# backend/users/permissions.py (新規作成)
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    管理者権限チェック
    
    - is_admin=True のユーザーのみ許可
    - 認証されていない場合は 401
    - 認証済みだが管理者でない場合は 403
    """
    
    message = '管理者権限が必要です'
    
    def has_permission(self, request, view):
        # 認証チェック（IsAuthenticated相当）
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 管理者チェック
        return request.user.is_admin
    
    def has_object_permission(self, request, view, obj):
        """オブジェクトレベルの権限チェック"""
        return request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    管理者: 全操作OK
    一般ユーザー: 読み取りのみ
    """
    
    message = 'この操作には管理者権限が必要です'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # GETは全員OK、その他は管理者のみ
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.is_admin