# backend/accounts/backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmployeeIdBackend(BaseBackend):
    """
    employee_id で認証するカスタムバックエンド
    
    - USERNAME_FIELD が employee_id のユーザーモデルに対応
    - 論理削除されたユーザーも検索対象（LoginAPIView で判定）
    - パスワードチェックのみ実施
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        認証処理
        
        Args:
            request: HTTPリクエスト
            username: employee_id（Django内部では username として扱われる）
            password: パスワード
        
        Returns:
            User: 認証成功時のユーザーインスタンス
            None: 認証失敗時
        """
        employee_id = username
        
        if employee_id is None or password is None:
            return None
        
        try:
            # 論理削除されたユーザーも検索対象
            # （is_active や deleted_at のチェックは LoginAPIView で実施）
            user = User.all_objects.get(employee_id=employee_id)
        except User.DoesNotExist:
            # 存在しないユーザー（タイミング攻撃対策のため処理時間を揃える）
            User().set_password(password)
            return None
        
        # パスワード検証
        if user.check_password(password):
            return user
        
        return None
    
    def get_user(self, user_id):
        """
        セッションからユーザーを取得
        
        Args:
            user_id: ユーザーID
        
        Returns:
            User: ユーザーインスタンス
            None: ユーザーが存在しない、または削除済みの場合
        """
        try:
            # ログインユーザーは削除済みを除外
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None