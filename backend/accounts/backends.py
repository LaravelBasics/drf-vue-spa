"""
グループ認証バックエンド

グループID + ユーザーID + パスワード の3点セットで認証
タイミング攻撃対策を実装
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class GroupUserAuthBackend(BaseBackend):
    """グループ + ユーザーID + パスワード認証バックエンド"""

    def authenticate(
        self, request, username=None, password=None, group_id=None, **kwargs
    ):
        """
        グループとユーザーIDとパスワードで認証

        Args:
            request: HTTPリクエスト
            username: ユーザーID
                Note: Django規約でパラメータ名は'username'だが、
                      実際の値はuser_id（プライマリキー）を受け取る
            password: パスワード
            group_id: グループID

        Returns:
            User: 認証成功時
            None: 認証失敗時
        """
        # usernameパラメータの値を内部的にuser_idとして扱う
        user_id = username

        # 必須パラメータチェック
        if not user_id or not password or not group_id:
            return None

        try:
            # ユーザー取得
            user = User.objects.filter(user_id=user_id).first()

            # ユーザー不在時のタイミング攻撃対策
            if user is None:
                User().set_password(password)
                return None

            # パスワード検証
            if not user.check_password(password):
                return None

            # グループ所属チェック
            if not user.groups_rel.filter(group_id=group_id, is_active=True).exists():
                return None

            # すべてのチェックをパス
            return user

        except Exception:
            # DB例外時もタイミング攻撃対策
            User().set_password(password)
            return None

    def get_user(self, user_id):
        """
        セッションからユーザー取得

        Args:
            user_id: ユーザーID（プライマリキー）

        Returns:
            User: ユーザー情報
            None: ユーザー不在
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
