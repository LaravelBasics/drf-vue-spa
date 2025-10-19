"""
カスタム認証バックエンド

社員番号（employee_id）でログインを行う認証バックエンド。
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmployeeIdBackend(BaseBackend):
    """Employee ID authentication backend"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        社員番号とパスワードで認証

        Args:
            request: HTTPリクエスト
            username: 社員番号（employee_id）
            password: パスワード

        Returns:
            User: 認証成功時
            None: 認証失敗時
        """
        employee_id = username

        if not employee_id or not password:
            return None

        try:
            user = User.objects.filter(employee_id=employee_id).first()

            if not user:
                # タイミング攻撃対策
                User().set_password(password)
                return None

            if user.check_password(password):
                return user

        except Exception:
            # タイミング攻撃対策
            User().set_password(password)

        return None

    def get_user(self, user_id):
        """
        セッションからユーザー取得

        Args:
            user_id: ユーザーID

        Returns:
            User: ユーザー情報
            None: ユーザー不在
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
