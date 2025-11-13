"""
ユーザー管理専用エラークラス
"""

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException


class UserServiceException(APIException):
    """
    ユーザーサービスエラー基底クラス

    Note:
        rest_framework.exceptions.APIExceptionを継承することで、
        DRFのエラーハンドラーが自動的に{"detail": "..."} 形式で返す
    """

    status_code = 400
    default_detail = "ユーザーサービスでエラーが発生しました。"
    default_code = "user_service_error"

    def __init__(self, detail=None, status_code=None):
        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail)


class LastAdminError(UserServiceException):
    """最後の管理者削除エラー"""

    status_code = 400

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
        super().__init__(detail=str(message))


class UserNotFoundError(UserServiceException):
    """ユーザー不在エラー"""

    status_code = 404

    def __init__(self):
        super().__init__(detail=str(_("ユーザーが見つかりません。")))


class CannotDeleteSelfError(UserServiceException):
    """自己削除エラー"""

    status_code = 400

    def __init__(self):
        super().__init__(detail=str(_("自分自身を削除することはできません。")))


class DeletedUserAccessError(UserServiceException):
    """削除済みユーザーアクセスエラー（同時操作対応）"""

    status_code = 404

    def __init__(self):
        super().__init__(detail=str(_("このユーザーは削除されています。")))
