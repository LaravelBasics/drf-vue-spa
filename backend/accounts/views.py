# backend/accounts/views.py
"""
認証関連のAPI（ログイン・ログアウト・現在のユーザー情報取得）

このファイルの役割:
1. CSRFトークン取得（セキュリティ対策）
2. ログイン処理（ブルートフォース攻撃対策付き）
3. ログアウト処理
4. ログイン中のユーザー情報を返す
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.core.cache import cache
from .serializers import LoginSerializer


# ============================================
# 1. CSRFトークン取得API
# ============================================
class CSRFView(APIView):
    """
    CSRFトークンを取得するAPI
    
    CSRFとは:
    - Cross-Site Request Forgery（クロスサイトリクエストフォージェリ）の略
    - 悪意のあるサイトから勝手にログインさせられる攻撃を防ぐ仕組み
    
    フロントエンドがやること:
    1. 最初にこのAPIを叩く（GET /api/accounts/csrf/）
    2. CSRFトークンを Cookie として受け取る
    3. 以降のPOSTリクエストでそのトークンを送る
    """
    permission_classes = [AllowAny]  # 誰でもアクセスOK

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        """CSRFトークンをCookieにセットして返す"""
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================
# 2. ログインAPI（メイン処理）
# ============================================
class LoginAPIView(APIView):
    """
    ログインAPI
    
    機能:
    1. 社員番号とパスワードでログイン
    2. ブルートフォース攻撃対策（連続ログイン失敗を検知）
    3. 削除済み・無効化されたユーザーの判定
    """
    permission_classes = [AllowAny]  # ログイン前なので誰でもアクセスOK
    
    # ==================== ブルートフォース対策の設定 ====================
    MAX_LOGIN_ATTEMPTS = 10  # 最大ログイン失敗回数
    LOCKOUT_DURATION = 60    # ロック時間（秒）= 1分間
    
    # ==================== キャッシュ管理（失敗回数を記録） ====================
    
    def _get_cache_key(self, employee_id):
        """
        失敗回数を保存するキーを生成
        
        例: 'login_attempts:EMP001'
        """
        return f'login_attempts:{employee_id}'
    
    def _get_lockout_key(self, employee_id):
        """
        ロック状態を保存するキーを生成
        
        例: 'login_locked:EMP001'
        """
        return f'login_locked:{employee_id}'
    
    def _increment_attempts(self, employee_id):
        """
        ログイン失敗回数を1増やす
        
        戻り値: 現在の失敗回数
        """
        cache_key = self._get_cache_key(employee_id)
        attempts = cache.get(cache_key, 0)  # 現在の回数を取得（なければ0）
        attempts += 1
        
        # キャッシュに保存（1時間で自動削除）
        cache.set(cache_key, attempts, 3600)
        return attempts
    
    def _is_locked(self, employee_id):
        """
        このユーザーがロック中かチェック
        
        戻り値: True = ロック中, False = ロックされていない
        """
        lockout_key = self._get_lockout_key(employee_id)
        return cache.get(lockout_key, False)
    
    def _lock_user(self, employee_id):
        """
        ユーザーをロック状態にする
        
        LOCKOUT_DURATION 秒間ログインできなくなる
        """
        lockout_key = self._get_lockout_key(employee_id)
        cache.set(lockout_key, True, self.LOCKOUT_DURATION)
    
    def _reset_attempts(self, employee_id):
        """
        ログイン成功時に失敗回数をリセット
        """
        cache_key = self._get_cache_key(employee_id)
        lockout_key = self._get_lockout_key(employee_id)
        cache.delete(cache_key)
        cache.delete(lockout_key)
    
    # ==================== メインのログイン処理 ====================
    
    def post(self, request):
        """
        ログイン処理
        
        フロントエンドから受け取るデータ:
        {
            "employee_id": "EMP001",
            "password": "password123"
        }
        """
        
        # ① データの検証（社員番号とパスワードが入力されているか）
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 入力されたデータを取得
        employee_id = serializer.validated_data.get('employee_id')
        password = serializer.validated_data.get('password')

        # ② ブルートフォース対策: ロック中かチェック
        if self._is_locked(employee_id):
            return Response(
                {
                    'error_code': 'ACCOUNT_LOCKED',
                    'detail': f'ログイン試行が{self.MAX_LOGIN_ATTEMPTS}回失敗しました。{self.LOCKOUT_DURATION}秒後に再度お試しください。'
                }, 
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # ③ 認証処理（backends.py の EmployeeIdBackend が実行される）
        user = authenticate(
            request,
            username=employee_id,  # 社員番号を渡す
            password=password
        )
        
        # ④ 認証成功の場合
        if user:
            # ④-1 削除済みユーザーチェック
            if hasattr(user, 'deleted_at') and user.deleted_at:
                self._increment_attempts(employee_id)  # 失敗回数を増やす
                return Response(
                    {
                        'error_code': 'ACCOUNT_DELETED',
                        'detail': 'このアカウントは削除されています'
                    }, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # ④-2 無効化されたユーザーチェック
            if not user.is_active:
                self._increment_attempts(employee_id)  # 失敗回数を増やす
                return Response(
                    {
                        'error_code': 'ACCOUNT_INACTIVE',
                        'detail': 'このアカウントは無効化されています'
                    }, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # ④-3 ログイン成功！
            self._reset_attempts(employee_id)  # 失敗回数をリセット
            login(request, user)  # セッションにユーザー情報を保存

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
        
        # ⑤ 認証失敗の場合（社員番号かパスワードが間違っている）
        attempts = self._increment_attempts(employee_id)  # 失敗回数を増やす
        
        # ⑥ 失敗回数が上限に達したらロック
        if attempts >= self.MAX_LOGIN_ATTEMPTS:
            self._lock_user(employee_id)
            return Response(
                {
                    'error_code': 'ACCOUNT_LOCKED',
                    'detail': f'ログイン試行が{self.MAX_LOGIN_ATTEMPTS}回失敗しました。{self.LOCKOUT_DURATION}秒後に再度お試しください。'
                }, 
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # ⑦ 通常のログイン失敗メッセージ
        return Response(
            {
                'error_code': 'INVALID_CREDENTIALS',
                'detail': '社員番号またはパスワードが正しくありません'
            }, 
            status=status.HTTP_401_UNAUTHORIZED
        )


# ============================================
# 3. ログアウトAPI
# ============================================
class LogoutAPIView(APIView):
    """
    ログアウトAPI
    
    やること:
    - セッション（Cookie）からログイン情報を削除
    """
    permission_classes = [IsAuthenticated]  # ログイン済みユーザーのみアクセスOK
    
    def post(self, request):
        """ログアウト処理"""
        try:
            logout(request)  # Djangoの標準ログアウト処理
            return Response({'detail': 'logged_out'})
        
        except Exception as e:
            # 万が一エラーが起きた場合
            return Response(
                {
                    'error_code': 'LOGOUT_FAILED',
                    'detail': 'ログアウトに失敗しました'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================
# 4. 現在のログインユーザー情報取得API
# ============================================
class MeAPIView(APIView):
    """
    ログイン中のユーザー情報を返す
    
    フロントエンドがやること:
    - ページ読み込み時にこのAPIを叩く
    - ログイン状態の確認とユーザー情報の取得
    """
    permission_classes = [IsAuthenticated]  # ログイン済みユーザーのみアクセスOK
    
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