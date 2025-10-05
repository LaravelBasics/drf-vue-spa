from django.contrib.auth.backends import BaseBackend # 👈 ModelBackend から BaseBackend に変更
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


class EmployeeIdBackend(BaseBackend): # 👈 ModelBackend から BaseBackend に変更
    """
    employee_id で認証するカスタムバックエンド
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        employee_id = username 
        
        if employee_id is None or password is None:
             return None
        
        try:
            # ⭐ 論理削除されたユーザーも検索できるよう all_objects を使用することが推奨
            #    Userモデルにall_objectsが定義されていることを前提
            user = User.all_objects.get(employee_id=employee_id) 
            
            # もし all_objects がない場合は、objects に戻して、ユーザーが存在するか確認
            # user = User.objects.get(employee_id=employee_id) 

        except User.DoesNotExist:
            return None
        
        # パスワード確認
        # user_can_authenticate は BaseBackend にはないため、シンプルにチェック
        if user.check_password(password):
            return user
        
        return None

    def get_user(self, user_id):
        """セッションからユーザーIDでユーザーを取得"""
        try:
            # ログインユーザーの取得は論理削除されていないユーザーを対象とする
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None