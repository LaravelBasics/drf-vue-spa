# backend/accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from .serializers import LoginSerializer
from audit.utils import create_audit_log


class CSRFView(APIView):
    """CSRFトークン取得"""
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginAPIView(APIView):
    """ログインAPI（監査ログ対応）"""
    """
    ログインAPI（employee_id認証対応）
    
    employee_id と password で認証を行います。
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )

        employee_id = serializer.validated_data.get('employee_id')
        password = serializer.validated_data.get('password')

        # ⭐ USERNAME_FIELD が employee_id なので、
        # authenticate の引数名も username として渡す（Djangoの仕様）
        user = authenticate(
            request,
            username=employee_id,  # Djangoの内部では username として扱われる
            password=password
        )
        
        if user:
            # 論理削除されているユーザーはログイン不可
            if hasattr(user, 'deleted_at') and user.deleted_at:
                # ⭐ ログイン失敗を記録
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
                        'error_code': 'ACCOUNT_DELETED',  # ⭐ エラーコード
                        'detail': 'このアカウントは削除されています'  # デフォルトメッセージ（フォールバック用）
                    }, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # アクティブでないユーザーはログイン不可
            if not user.is_active:
                # ⭐ ログイン失敗を記録
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
                        'error_code': 'ACCOUNT_INACTIVE',  # ⭐ エラーコード
                        'detail': 'このアカウントは無効化されています'
                    }, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            login(request, user)

            # ⭐ ログイン成功を記録
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
        
        # ⭐ ログイン失敗を記録（ユーザー不明）
        create_audit_log(
            action='LOGIN_FAILED',
            model_name='User',
            success=False,
            error_message=f'認証失敗: {employee_id}',
            request=request
        )

        return Response(
            {
                'error_code': 'INVALID_CREDENTIALS',  # ⭐ エラーコード
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
                    'error_code': 'LOGOUT_FAILED',  # ⭐ エラーコード
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