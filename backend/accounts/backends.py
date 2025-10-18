"""
カスタム認証バックエンド

このファイルの役割:
- デフォルトの「username」ではなく「employee_id（社員番号）」でログイン
- パスワードの検証を行う
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

# カスタムユーザーモデルを取得（settings.AUTH_USER_MODEL で指定）
User = get_user_model()


class EmployeeIdBackend(BaseBackend):
    """
    社員番号（employee_id）でログインするための認証バックエンド
    
    処理の流れ:
    1. 社員番号でユーザーを検索
    2. パスワードが一致するか確認
    3. 一致すればユーザー情報を返す
    
    注意:
    - 削除済み・無効化されたユーザーの判定は views.py で行う
    - ここでは認証のみを担当
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        社員番号とパスワードで認証
        
        引数:
            request: HTTPリクエスト（未使用だが必須）
            username: 社員番号（Django内部では username と呼ばれる）
            password: パスワード
        
        戻り値:
            User: 認証成功時
            None: 認証失敗時
        """
        
        # わかりやすいように変数名を変更
        employee_id = username
        
        # 社員番号またはパスワードが未入力なら失敗
        if not employee_id or not password:
            return None
        
        try:
            # 社員番号でユーザーを検索
            # all_objects: 削除済みユーザーも含めて検索
            #（削除済み判定は views.py で行うため）
            user = User.all_objects.get(employee_id=employee_id)
        
        except User.DoesNotExist:
            # ユーザーが存在しない場合
            
            # セキュリティ対策: タイミング攻撃を防ぐため、
            # 存在しないユーザーでもパスワード処理を実行
            # （処理時間から「ユーザーの存在」を推測されないようにする）
            User().set_password(password)
            return None
        
        # パスワードが一致するか確認
        if user.check_password(password):
            return user
        
        # パスワード不一致
        return None
    
    
    def get_user(self, user_id):
        """
        セッションからログインユーザーを取得
        
        役割:
        - ページ遷移時に「このユーザーはログイン済みか」を確認
        - セッション（Cookie）に保存されたユーザーIDから情報を取得
        
        引数:
            user_id: セッションに保存されているユーザーID
        
        戻り値:
            User: ユーザー情報
            None: ユーザーが存在しない（削除済み）
        """
        try:
            # 削除されていないユーザーのみ取得
            # 削除済みユーザーは自動的にログアウトされる
            return User.objects.get(pk=user_id)
        
        except User.DoesNotExist:
            return None