# backend/accounts/views.py
"""
認証関連のAPI（翻訳対応版）

改善ポイント:
1. すべてのエラーメッセージを gettext_lazy で翻訳対応
2. エラーメッセージの一貫性を確保
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from .serializers import LoginSerializer
from django.conf import settings


class CSRFView(APIView):
    """CSRFトークンを取得するAPI"""
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        """CSRFトークンをCookieにセットして返す"""
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginAPIView(APIView):
    """ログインAPI（翻訳対応）"""
    permission_classes = [AllowAny]
    
    MAX_LOGIN_ATTEMPTS = settings.LOGIN_MAX_ATTEMPTS
    LOCKOUT_DURATION = settings.LOGIN_LOCKOUT_DURATION

    # キャッシュキーのプレフィックス
    CACHE_KEY_PREFIX = 'login_attempts'
    LOCKOUT_KEY_PREFIX = 'login_locked'
    
    def _get_cache_key(self, employee_id):
        return f'{self.CACHE_KEY_PREFIX}:{employee_id}'
    
    def _get_lockout_key(self, employee_id):
        return f'{self.LOCKOUT_KEY_PREFIX}:{employee_id}'
    
    def _increment_attempts(self, employee_id):
        cache_key = self._get_cache_key(employee_id)
        attempts = cache.get(cache_key, 0)
        attempts += 1
        cache.set(cache_key, attempts, 3600)
        return attempts
    
    def _is_locked(self, employee_id):
        lockout_key = self._get_lockout_key(employee_id)
        return cache.get(lockout_key, False)
    
    def _lock_user(self, employee_id):
        lockout_key = self._get_lockout_key(employee_id)
        cache.set(lockout_key, True, self.LOCKOUT_DURATION)
    
    def _reset_attempts(self, employee_id):
        cache_key = self._get_cache_key(employee_id)
        lockout_key = self._get_lockout_key(employee_id)
        cache.delete(cache_key)
        cache.delete(lockout_key)
    
    def post(self, request):
        """ログイン処理（翻訳対応）"""
        
        # ① データの検証
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )

        employee_id = serializer.validated_data.get('employee_id')
        password = serializer.validated_data.get('password')

        # ② ブルートフォース対策: ロック中かチェック
        if self._is_locked(employee_id):
            return Response(
                {
                    'error_code': 'ACCOUNT_LOCKED',
                    'detail': str(_('ログイン試行が%(max_attempts)d回失敗しました。%(lockout_duration)d秒後に再度お試しください') % {
                        'max_attempts': self.MAX_LOGIN_ATTEMPTS,
                        'lockout_duration': self.LOCKOUT_DURATION
                    })
                }, 
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # ③ 認証処理
        user = authenticate(
            request,
            username=employee_id,
            password=password
        )
        
        # ④ 認証成功の場合
        if user:
            # ④-1 削除済みユーザーチェック
            if hasattr(user, 'deleted_at') and user.deleted_at:
                self._increment_attempts(employee_id)
                return Response(
                    {
                        'error_code': 'ACCOUNT_DELETED',
                        'detail': str(_('このアカウントは削除されています'))
                    }, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # ④-2 無効化されたユーザーチェック
            if not user.is_active:
                self._increment_attempts(employee_id)
                return Response(
                    {
                        'error_code': 'ACCOUNT_INACTIVE',
                        'detail': str(_('このアカウントは無効化されています'))
                    }, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # ④-3 ログイン成功！
            self._reset_attempts(employee_id)
            login(request, user)

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
        
        # ⑤ 認証失敗の場合
        attempts = self._increment_attempts(employee_id)
        
        # ⑥ 失敗回数が上限に達したらロック
        if attempts >= self.MAX_LOGIN_ATTEMPTS:
            self._lock_user(employee_id)
            return Response(
                {
                    'error_code': 'ACCOUNT_LOCKED',
                    'detail': str(_('ログイン試行が%(max_attempts)d回失敗しました。%(lockout_duration)d秒後に再度お試しください') % {
                        'max_attempts': self.MAX_LOGIN_ATTEMPTS,
                        'lockout_duration': self.LOCKOUT_DURATION
                    })
                }, 
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # ⑦ 通常のログイン失敗メッセージ
        return Response(
            {
                'error_code': 'INVALID_CREDENTIALS',
                'detail': str(_('社員番号またはパスワードが正しくありません'))
            }, 
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutAPIView(APIView):
    """ログアウトAPI"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """ログアウト処理"""
        try:
            logout(request)
            return Response({'detail': 'logged_out'})
        
        except Exception as e:
            return Response(
                {
                    'error_code': 'LOGOUT_FAILED',
                    'detail': str(_('ログアウトに失敗しました'))
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MeAPIView(APIView):
    """ログイン中のユーザー情報を返す"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """現在のユーザー情報を返す"""
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


# ==================== 変更点のまとめ ====================
"""
✅ 改善ポイント:

1. gettext_lazy のインポート
   from django.utils.translation import gettext_lazy as _

2. すべてのエラーメッセージを翻訳対応
   - '社員番号またはパスワードが正しくありません'
     → str(_('社員番号またはパスワードが正しくありません'))
   
   - 'このアカウントは削除されています'
     → str(_('このアカウントは削除されています'))
   
   - ロックメッセージも % フォーマットで翻訳対応

3. str() でラップする理由
   - gettext_lazy は「遅延翻訳オブジェクト」を返す
   - 明示的に文字列化することで意図を明確にする
   - DRF は自動変換するが、str() で確実性を高める

注意点:
- % フォーマットは Python 標準の文字列フォーマット
- Django の翻訳システムと併用可能
- 処理順序:
  1. _('...%(max_attempts)d...') で翻訳文字列を取得
  2. % {...} でプレースホルダーに値を埋め込む
  3. str() で明示的に文字列化（DRF は自動変換するが確実性を高める）
"""