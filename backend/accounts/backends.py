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
            username: ユーザーID（DRF規約でusernameだが実際はuser_id）
            password: パスワード
            group_id: グループID（新規追加）

        Returns:
            User: 認証成功時
            None: 認証失敗時
        """
        user_id = username

        # 必須パラメータチェック
        if not user_id or not password or not group_id:
            return None

        try:
            # ユーザー存在チェック
            user = User.objects.filter(user_id=user_id).first()

            if user is None:
                # ユーザー不在時のタイミング攻撃対策
                User().set_password(password)
                return None

            # パスワード検証
            if not user.check_password(password):
                return None

            # ✅ グループ所属チェック（重要！）
            # このユーザーが指定されたグループに所属しているか確認
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
            user_id: ユーザーID

        Returns:
            User: ユーザー情報
            None: ユーザー不在
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
