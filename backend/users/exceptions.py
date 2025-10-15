# backend/users/exceptions.py
"""
ユーザー管理専用のエラー（例外）クラス

このファイルの役割:
- ユーザー管理で発生するエラーを定義
- エラーコードと日本語メッセージをセットで管理
- フロントエンドに統一されたエラー形式を返す

なぜ専用のエラークラスが必要？:
- 「最後の管理者を削除しようとした」など、業務特有のエラーを表現
- エラーコードで多言語対応しやすい
- views.py でキャッチしてJSON形式で返せる
"""


# ==================== 基底クラス ====================

class UserServiceException(Exception):
    """
    ユーザーサービスのエラー基底クラス
    
    すべてのユーザー管理エラーの親クラス
    共通の属性（error_code, detail, status_code）を持つ
    """
    
    def __init__(self, error_code, detail, status_code=400):
        """
        引数:
            error_code: エラーコード（例: 'LAST_ADMIN', 'NOT_FOUND'）
                       フロントエンドがこのコードで翻訳メッセージを表示
            detail: 詳細メッセージ（日本語でOK）
            status_code: HTTPステータスコード
                        400 = Bad Request（入力エラー）
                        404 = Not Found（見つからない）
                        500 = Server Error（サーバーエラー）
        """
        self.error_code = error_code
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


# ==================== 具体的なエラークラス ====================

class LastAdminError(UserServiceException):
    """
    最後の管理者を削除・無効化しようとした時のエラー
    
    発生タイミング:
    - 最後の1人の管理者を削除しようとした
    - 最後の1人の管理者から管理者権限を外そうとした
    - 最後の1人の管理者を無効化しようとした
    
    使い方:
    raise LastAdminError(action='削除')
    → 「管理者は最低1人必要です。最後の管理者を削除することはできません。」
    """
    
    def __init__(self, action='削除'):
        """
        引数:
            action: 何をしようとしたか（'削除', '管理者権限から外す', '無効化'）
        """
        super().__init__(
            error_code='LAST_ADMIN',
            detail=f'管理者は最低1人必要です。最後の管理者を{action}することはできません。',
            status_code=400
        )


class UserNotFoundError(UserServiceException):
    """
    ユーザーが見つからない時のエラー
    
    発生タイミング:
    - 存在しないIDでユーザーを取得しようとした
    - 削除済みユーザーを復元しようとしたが見つからない
    
    使い方:
    raise UserNotFoundError()
    """
    
    def __init__(self):
        super().__init__(
            error_code='NOT_FOUND',
            detail='ユーザーが見つかりません。',
            status_code=404
        )


class CannotDeleteSelfError(UserServiceException):
    """
    自分自身を削除しようとした時のエラー
    
    発生タイミング:
    - ログイン中のユーザーが自分自身を削除しようとした
    
    業務ルール:
    - 自分で自分を削除するのは危険なので禁止
    - 他の管理者に削除してもらう必要がある
    
    使い方:
    raise CannotDeleteSelfError()
    """
    
    def __init__(self):
        super().__init__(
            error_code='CANNOT_DELETE_SELF',
            detail='自分自身を削除することはできません。',
            status_code=400
        )


class CannotUpdateDeletedError(UserServiceException):
    """
    削除済みユーザーを編集しようとした時のエラー
    
    発生タイミング:
    - 論理削除済みのユーザーを更新しようとした
    
    業務ルール:
    - 削除済みユーザーは編集できない
    - 先に復元してから編集する必要がある
    
    使い方:
    raise CannotUpdateDeletedError()
    """
    
    def __init__(self):
        super().__init__(
            error_code='CANNOT_UPDATE_DELETED',
            detail='削除済みユーザーは編集できません。',
            status_code=400
        )


# ==================== 使用例 ====================
"""
views.py での使い方:

try:
    UserService.delete_user(user, request.user.id)
except UserServiceException as e:
    # エラー情報を取得
    return Response(
        {
            'error_code': e.error_code,  # 'LAST_ADMIN'
            'detail': e.detail           # '管理者は最低1人必要です...'
        },
        status=e.status_code             # 400
    )
"""