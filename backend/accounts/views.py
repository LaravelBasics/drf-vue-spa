# backend/accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from .serializers import LoginSerializer


class CSRFView(APIView):
    """CSRFトークン取得"""
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginAPIView(APIView):
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
                return Response(
                    {'detail': 'このアカウントは削除されています'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # アクティブでないユーザーはログイン不可
            if not user.is_active:
                return Response(
                    {'detail': 'このアカウントは無効化されています'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
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
        
        return Response(
            {'detail': '社員コードまたはパスワードが正しくありません'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutAPIView(APIView):
    """ログアウトAPI"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'detail': 'logged_out'})


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