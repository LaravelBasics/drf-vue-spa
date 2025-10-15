# backend/accounts/backends.py
"""
カスタム認証バックエンド

このファイルの役割:
- 通常の Django は「username」でログインするが、
  このアプリでは「employee_id（社員番号）」でログインする
- パスワードが正しいかチェックする
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

# Userモデルを取得（settings.py で指定したカスタムユーザー）
User = get_user_model()


class EmployeeIdBackend(BaseBackend):
    """
    社員番号（employee_id）でログインするための認証システム
    
    やること:
    1. 社員番号でユーザーを探す
    2. パスワードが合っているか確認する
    3. 合っていればログイン成功
    
    やらないこと:
    - 削除済み・無効化されたユーザーの判定
      （それは views.py の LoginAPIView でやる）
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        ログイン認証を行う（社員番号 + パスワード）
        
        引数:
            request: リクエスト情報（使わないけど必須）
            username: ログイン時に入力された社員番号
                     （Django内部では「username」と呼ばれるが、実際は employee_id）
            password: ログイン時に入力されたパスワード
        
        戻り値:
            成功時: ユーザー情報
            失敗時: None
        """
        
        # わかりやすいように変数名を変更
        employee_id = username
        
        # 社員番号かパスワードが空ならログイン失敗
        if employee_id is None or password is None:
            return None
        
        try:
            # ① 社員番号でユーザーを探す
            # 注意: all_objects を使うことで削除済みユーザーも検索対象にする
            #      （削除済み判定は LoginAPIView で行うため）
            user = User.all_objects.get(employee_id=employee_id)
        
        except User.DoesNotExist:
            # ユーザーが見つからない場合
            
            # セキュリティ対策: わざとパスワード処理を実行
            # 理由: 「ユーザーが存在するか」を処理時間から推測されないようにする
            #      （存在しないユーザーでも処理時間を同じにする）
            User().set_password(password)
            return None
        
        # ② パスワードが正しいか確認
        if user.check_password(password):
            # パスワードが合っていればユーザー情報を返す
            return user
        
        # パスワードが間違っていたら None を返す
        return None
    
    
    def get_user(self, user_id):
        """
        セッションからログインユーザーを取得
        
        このメソッドの役割:
        - ページ遷移するたびに「このユーザーはログイン済みか？」を確認する
        - セッション（Cookie）に保存されたユーザーIDから情報を取得
        
        引数:
            user_id: セッションに保存されているユーザーID
        
        戻り値:
            ユーザー情報 or None（削除済み・存在しない場合）
        """
        try:
            # ログイン中のユーザーは削除済みを除外
            # （削除されたユーザーは自動的にログアウトさせる）
            return User.objects.get(pk=user_id)
        
        except User.DoesNotExist:
            # ユーザーが見つからない = 削除されたのでログアウト
            return None