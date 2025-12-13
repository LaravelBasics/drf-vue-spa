# accounts/backends.py
"""
レガシーシステム対応 グループ認証バックエンド

特徴:
- 文字列主キー対応（user_id, group_id）
- グループID + ユーザーID + パスワード の3点認証
- タイミング攻撃対策実装
- inspectdb取り込みモデル対応
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from common.models import MUserGroup

User = get_user_model()


class GroupUserAuthBackend(BaseBackend):
    """
    文字列PK + グループ認証バックエンド

    認証方式:
    1. ユーザーID + パスワード認証
    2. グループ所属確認
    3. アクティブチェック

    セキュリティ:
    - タイミング攻撃対策実装済み
    """

    def authenticate(
        self, request, username=None, password=None, group_id=None, **kwargs
    ):
        """
        グループ + ユーザーID + パスワード認証

        Args:
            request: HTTPリクエスト
            username: ユーザーID（★Django規約でパラメータ名はusername★）
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
            # ★1. ユーザー取得（文字列PKで検索）★
            user = User.objects.filter(user_id=user_id).first()

            # ★タイミング攻撃対策★
            # ユーザー不在でも同じ処理時間を確保
            if user is None:
                User().set_password(password)
                return None

            # ★2. パスワード検証★
            if not user.check_password(password):
                return None

            # ★3. グループ所属チェック（手動JOIN）★
            # ForeignKey使えないので、文字列フィールドで直接検索
            group_exists = MUserGroup.objects.filter(
                user_id=user.user_id, group_id=group_id, is_active=True
            ).exists()

            if not group_exists:
                return None

            # ★4. ユーザーアクティブチェック★
            if not user.is_active:
                return None

            # すべてのチェックをパス
            return user

        except Exception:
            # DB例外時もタイミング攻撃対策
            User().set_password(password)
            return None

    def get_user(self, user_id):
        """
        ★超重要★ セッションからユーザー復元

        Django内部で呼ばれるメソッド。
        user_idを文字列のまま扱う（int変換しない）

        Args:
            user_id: ユーザーID（文字列型の主キー）

        Returns:
            User: ユーザー情報
            None: ユーザー不在
        """
        try:
            # ★文字列PKでユーザー取得★
            user = User.objects.get(pk=user_id)

            # is_activeチェック
            if user.is_active:
                return user
            return None

        except User.DoesNotExist:
            return None

    def user_can_authenticate(self, user):
        """ユーザーが認証可能かチェック"""
        return user.is_active
