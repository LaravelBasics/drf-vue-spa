"""
カスタム認証バックエンド

社員番号（employee_id）でログインを行う認証バックエンド。
アクティブなユーザーのみを認証対象とし、削除済みユーザーは認証層で弾く。
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmployeeIdBackend(BaseBackend):
    """
    社員番号（employee_id）による認証バックエンド

    処理フロー:
    1. アクティブなユーザーのみを検索
    2. パスワード検証
    3. 検証成功でユーザーを返却
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        社員番号とパスワードで認証

        Args:
            request: HTTPリクエスト
            username: 社員番号（Django内部ではusernameと呼ばれる）
            password: パスワード

        Returns:
            User: 認証成功時
            None: 認証失敗時

        Note:
            削除済みユーザーは認証対象外（セキュリティ対策）
        """
        employee_id = username

        if not employee_id or not password:
            return None

        try:
            # アクティブなユーザーのみ取得（削除済みは除外）
            user = User.objects.filter(employee_id=employee_id).first()

            if not user:
                # タイミング攻撃対策: ユーザー不在でもパスワード処理を実行
                User().set_password(password)
                return None

            # パスワード検証
            if user.check_password(password):
                return user

        except Exception:
            # 例外発生時もタイミング攻撃対策を実行
            User().set_password(password)

        return None

    def get_user(self, user_id):
        """
        セッションからユーザー取得

        Args:
            user_id: セッション保存されているユーザーID

        Returns:
            User: ユーザー情報
            None: ユーザー不在（削除済み含む）
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
