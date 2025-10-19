"""
ユーザー管理権限チェック
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """管理者のみアクセス許可"""

    message = "管理者権限が必要です"

    def has_permission(self, request, view):
        """APIアクセス権限チェック"""
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.is_admin

    def has_object_permission(self, request, view, obj):
        """オブジェクトアクセス権限チェック"""
        return request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    """管理者は全操作、一般ユーザーは閲覧のみ"""

    message = "この操作には管理者権限が必要です"

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_admin
