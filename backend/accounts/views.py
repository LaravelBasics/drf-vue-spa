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
    """ログインAPI"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )

        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({
                'detail': 'logged_in',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'is_admin': user.is_admin,
                }
            })
        
        return Response(
            {'detail': 'ユーザー名またはパスワードが正しくありません'}, 
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
            'username': user.username,
            'email': user.email,
            'employee_id': getattr(user, 'employee_id', None),
            'is_admin': getattr(user, 'is_admin', False),
        })