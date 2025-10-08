# backend/users/views.py (修正版)
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F
from django.db.models.functions import Collate

from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from .services.user_service import UserService
from .permissions import IsAdminUser  # ⭐ 追加

User = get_user_model()


# カスタムページネーションクラス
class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10


class UserViewSet(viewsets.ModelViewSet):
    """ユーザー管理ViewSet（論理削除対応・employee_id認証）"""
    
    queryset = User.objects.all()
    
    # ⭐ 管理者権限必須に変更
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    
    # search_fields = ['^employee_id', 'username']これだと検索パターンが２つになる
    search_fields = ['^username']

    filterset_fields = ['is_admin', 'is_active']
    ordering_fields = ['username', 'employee_id', 'created_at', 'is_admin', 'id']
    ordering = ['id']
    
    def get_queryset(self):
        """日本語ソート対応のクエリセット"""
        queryset = super().get_queryset()
        
        ordering_param = self.request.query_params.get('ordering', '')
        
        if 'username' in ordering_param:
            if ordering_param == 'username':
                queryset = queryset.order_by(F('username').asc(nulls_last=True))
            else:
                queryset = queryset.order_by(F('username').desc(nulls_last=True))
        
        return queryset

    def get_serializer_class(self):
        """アクションに応じてシリアライザーを選択"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    # ⭐ 権限チェック強化（念のため）
    def check_admin_permission(self):
        """管理者権限チェック（追加の安全装置）"""
        if not self.request.user.is_admin:
            raise PermissionDenied('この操作には管理者権限が必要です')
    
    def create(self, request, *args, **kwargs):
        """ユーザー作成"""
        self.check_admin_permission()  # ⭐ 念のため明示的チェック
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = UserService.create_user(serializer.validated_data)
        
        response_serializer = UserSerializer(user)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """ユーザー更新"""
        self.check_admin_permission()
        
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        try:
            user = UserService.update_user(instance, serializer.validated_data)
        except ValidationError as e:
            return Response(
                {'error': str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response_serializer = UserSerializer(user)
        return Response(response_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """ユーザー削除（論理削除）"""
        self.check_admin_permission()
        
        instance = self.get_object()
        
        try:
            UserService.delete_user(instance)
        except ValidationError as e:
            return Response(
                {'error': str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """一括削除（論理削除）"""
        self.check_admin_permission()
        
        user_ids = request.data.get('ids', [])
        
        if not user_ids:
            return Response(
                {'error': '削除対象のIDを指定してください'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            deleted_count = UserService.bulk_delete_users(user_ids)
            return Response({
                'message': f'{deleted_count}件のユーザーを削除しました',
                'deleted_count': deleted_count
            })
        except ValidationError as e:
            return Response(
                {'error': str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """ユーザー復元"""
        self.check_admin_permission()
        
        try:
            user = UserService.restore_user(pk)
            serializer = UserSerializer(user)
            return Response({
                'message': 'ユーザーを復元しました',
                'user': serializer.data
            })
        except User.DoesNotExist:
            return Response(
                {'error': '対象のユーザーが見つかりません'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def bulk_restore(self, request):
        """一括復元"""
        self.check_admin_permission()
        
        user_ids = request.data.get('ids', [])
        
        if not user_ids:
            return Response(
                {'error': '復元対象のIDを指定してください'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        restored_count = UserService.bulk_restore_users(user_ids)
        return Response({
            'message': f'{restored_count}件のユーザーを復元しました',
            'restored_count': restored_count
        })
    
    @action(detail=False, methods=['get'])
    def deleted(self, request):
        """削除済みユーザー一覧"""
        self.check_admin_permission()
        
        deleted_users = User.all_objects.filter(deleted_at__isnull=False)
        deleted_users = self.filter_queryset(deleted_users)
        
        page = self.paginate_queryset(deleted_users)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserSerializer(deleted_users, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """ユーザー統計情報（高速化版）"""
        self.check_admin_permission()
        
        from django.db.models import Count, Q
        
        stats = User.objects.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(is_active=True)),
            admins=Count('id', filter=Q(is_admin=True, is_active=True))
        )
        
        deleted_count = User.all_objects.filter(deleted_at__isnull=False).count()
        
        return Response({
            'total_users': stats['total'],
            'active_users': stats['active'],
            'admin_users': stats['admins'],
            'deleted_users': deleted_count,
        })