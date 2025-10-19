"""
ユーザー管理専用エラークラス
"""

from django.utils.translation import gettext_lazy as _


class UserServiceException(Exception):
    """ユーザーサービスエラー基底クラス"""

    def __init__(self, error_code, detail, status_code=400):
        """
        Args:
            error_code: エラーコード（例: 'LAST_ADMIN'）
            detail: エラーメッセージ
            status_code: HTTPステータスコード
        """
        self.error_code = error_code
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class LastAdminError(UserServiceException):
    """最後の管理者削除エラー"""

    def __init__(self, action="削除"):
        super().__init__(
            error_code="LAST_ADMIN",
            detail=f"管理者は最低1人必要です。最後の管理者を{action}することはできません。",
            status_code=400,
        )


class UserNotFoundError(UserServiceException):
    """ユーザー不在エラー"""

    def __init__(self):
        super().__init__(
            error_code="NOT_FOUND", detail="ユーザーが見つかりません。", status_code=404
        )


class CannotDeleteSelfError(UserServiceException):
    """自己削除エラー"""

    def __init__(self):
        super().__init__(
            error_code="CANNOT_DELETE_SELF",
            detail=_("自分自身を削除することはできません。"),
            status_code=400,
        )


class CannotUpdateDeletedError(UserServiceException):
    """削除済み編集エラー"""

    def __init__(self):
        super().__init__(
            error_code="CANNOT_UPDATE_DELETED",
            detail=_("削除済みユーザーは編集できません。"),
            status_code=400,
        )
