# backend/accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.core.cache import cache
from .serializers import LoginSerializer
from audit.utils import create_audit_log


class CSRFView(APIView):
    """CSRFトークン取得"""
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginAPIView(APIView):
    """ログインAPI（ブルートフォース対策 + 監査ログ対応）"""
    permission_classes = [AllowAny]
    
    # ⭐ ブルートフォース対策の設定
    MAX_LOGIN_ATTEMPTS = 10 # 最大試行回数
    LOCKOUT_DURATION = 60  # 秒（1分）
    
    def _get_cache_key(self, employee_id):
        """キャッシュキーを生成"""
        return f'login_attempts:{employee_id}'
    
    def _get_lockout_key(self, employee_id):
        """ロック状態のキャッシュキーを生成"""
        return f'login_locked:{employee_id}'
    
    def _increment_attempts(self, employee_id):
        """ログイン試行回数をインクリメント"""
        cache_key = self._get_cache_key(employee_id)
        attempts = cache.get(cache_key, 0)
        attempts += 1
        # キャッシュを更新（1時間で自動削除）
        cache.set(cache_key, attempts, 3600)
        return attempts
    
    def _is_locked(self, employee_id):
        """ユーザーがロック状態か確認"""
        lockout_key = self._get_lockout_key(employee_id)
        return cache.get(lockout_key, False)
    
    def _lock_user(self, employee_id):
        """ユーザーをロック"""
        lockout_key = self._get_lockout_key(employee_id)
        cache.set(lockout_key, True, self.LOCKOUT_DURATION)
    
    def _reset_attempts(self, employee_id):
        """ログイン試行回数をリセット"""
        cache_key = self._get_cache_key(employee_id)
        lockout_key = self._get_lockout_key(employee_id)
        cache.delete(cache_key)
        cache.delete(lockout_key)
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )

        employee_id = serializer.validated_data.get('employee_id')
        password = serializer.validated_data.get('password')

        # ⭐ ブルートフォース対策: ロック状態を確認
        if self._is_locked(employee_id):
            create_audit_log(
                action='LOGIN_FAILED',
                model_name='User',
                success=False,
                error_message=f'アカウントロック中: {employee_id}',
                request=request
            )
            return Response(
                {
                    'error_code': 'ACCOUNT_LOCKED',
                }, 
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        user = authenticate(
            request,
            username=employee_id,
            password=password
        )
        
        if user:
            # ⭐ ログイン成功: 試行回数をリセット
            if hasattr(user, 'deleted_at') and user.deleted_at:
                self._increment_attempts(employee_id)
                create_audit_log(
                    action='LOGIN_FAILED',
                    model_name='User',
                    object_id=user.id,
                    success=False,
                    error_message='削除されたアカウント',
                    request=request
                )
                return Response(
                    {
                        'error_code': 'ACCOUNT_DELETED',
                        'detail': 'このアカウントは削除されています'
                    }, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            if not user.is_active:
                self._increment_attempts(employee_id)
                create_audit_log(
                    action='LOGIN_FAILED',
                    model_name='User',
                    object_id=user.id,
                    success=False,
                    error_message='無効化されたアカウント',
                    request=request
                )
                return Response(
                    {
                        'error_code': 'ACCOUNT_INACTIVE',
                        'detail': 'このアカウントは無効化されています'
                    }, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # ⭐ ログイン成功
            self._reset_attempts(employee_id)
            login(request, user)

            create_audit_log(
                action='LOGIN',
                model_name='User',
                object_id=user.id,
                request=request
            )
            return Response({
                'detail': 'logged_in',
                'user': {
                    'id': user.id,
                    'employee_id': user.employee_id,
                    'username': user.username,
                    'email': user.email,
                    'display_name': user.display_name,
                    'is_admin': user.is_admin,
                }
            })
        
        # ⭐ ログイン失敗: 試行回数をインクリメント
        attempts = self._increment_attempts(employee_id)
        
        # ⭐ ロック判定
        if attempts >= self.MAX_LOGIN_ATTEMPTS:
            self._lock_user(employee_id)
            create_audit_log(
                action='LOGIN_FAILED',
                model_name='User',
                success=False,
                error_message=f'ブルートフォース攻撃検出（試行回数超過）: {employee_id}',
                request=request
            )
            return Response(
                {
                    'error_code': 'ACCOUNT_LOCKED',
                    'detail': f'ログイン試行が{self.MAX_LOGIN_ATTEMPTS}回失敗しました。{self.LOCKOUT_DURATION}秒後に再度お試しください。'
                }, 
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        create_audit_log(
            action='LOGIN_FAILED',
            model_name='User',
            success=False,
            error_message=f'認証失敗: {employee_id}',
            request=request
        )

        return Response(
            {
                'error_code': 'INVALID_CREDENTIALS',
                'detail': '社員番号またはパスワードが正しくありません'
            }, 
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutAPIView(APIView):
    """ログアウトAPI"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            create_audit_log(
                action='LOGOUT',
                model_name='User',
                object_id=request.user.id,
                request=request
            )
            logout(request)
            return Response({'detail': 'logged_out'})
        except Exception as e:
            return Response(
                {
                    'error_code': 'LOGOUT_FAILED',
                    'detail': 'ログアウトに失敗しました'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MeAPIView(APIView):
    """現在のユーザー情報取得"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'employee_id': user.employee_id,
            'username': user.username,
            'email': user.email,
            'display_name': user.display_name,
            'is_admin': user.is_admin,
            'is_active': user.is_active,
        })