# backend/api/views.py
# from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import LoginSerializer # 👈 インポートを追加

class CSRFView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    # Serializerを使ってデータのバリデーションを行う
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # バリデーションが成功したら、validated_dataからデータを取得
    username = serializer.validated_data.get('username')
    password = serializer.validated_data.get('password')

    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return Response({'detail':'logged_in'})
    
    return Response({'detail':'ユーザー名かパスワードが違います'}, status=status.HTTP_401_UNAUTHORIZED)
@api_view(['POST'])
def logout_api(request):
    logout(request)
    return Response({'detail':'logged_out'})

@api_view(['GET'])
def me_api(request):
    if not request.user.is_authenticated:
        return Response({'detail':'unauthenticated'}, status=401)
    return Response({'username': request.user.username, 'email': request.user.email})