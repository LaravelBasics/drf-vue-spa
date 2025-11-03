"""
ユーザー管理専用エラークラス
"""

from django.utils.translation import gettext_lazy as _


class UserServiceException(Exception):
    """ユーザーサービスエラー基底クラス"""

    def __init__(self, detail, status_code=400):
        """
        Args:
            detail: エラーメッセージ
            status_code: HTTPステータスコード
        """
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class LastAdminError(UserServiceException):
    """最後の管理者削除エラー"""

    def __init__(self, action="delete"):
        # アクションごとに翻訳可能なメッセージを定義
        messages = {
            "delete": _(
                "管理者は最低1人必要です。最後の管理者を削除することはできません。"
            ),
            "demote": _(
                "管理者は最低1人必要です。最後の管理者から管理者権限を外すことはできません。"
            ),
            "deactivate": _(
                "管理者は最低1人必要です。最後の管理者を無効化することはできません。"
            ),
        }

        message = messages.get(action, messages["delete"])
        super().__init__(detail=str(message), status_code=400)


class UserNotFoundError(UserServiceException):
    """ユーザー不在エラー"""

    def __init__(self):
        super().__init__(
            detail=str(_("ユーザーが見つかりません。")),
            status_code=404,
        )


class CannotDeleteSelfError(UserServiceException):
    """自己削除エラー"""

    def __init__(self):
        super().__init__(
            detail=str(_("自分自身を削除することはできません。")),
            status_code=400,
        )


class CannotUpdateDeletedError(UserServiceException):
    """削除済み編集エラー"""

    def __init__(self):
        super().__init__(
            detail=str(_("削除済みユーザーは編集できません。")),
            status_code=400,
        )
