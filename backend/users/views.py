# backend/users/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, Count, Q

from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from .services.user_service import UserService
from .permissions import IsAdminUser

User = get_user_model()


class UserPagination(PageNumberPagination):
    """ユーザー一覧のページネーション設定"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    """
    ユーザー管理ViewSet
    
    機能:
    - CRUD操作（論理削除対応）
    - 一括削除・復元
    - 削除済みユーザー一覧
    - 統計情報取得
    - 日本語ソート対応
    """
    
    queryset = User.objects.all()
    pagination_class = UserPagination
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    # フィルター・検索・ソート設定
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_admin', 'is_active']
    
    # 検索: employee_id（前方一致）or username（部分一致）
    search_fields = ['^employee_id', 'username']
    
    ordering_fields = ['id', 'employee_id', 'username', 'created_at', 'is_admin']
    ordering = ['id']
    
    def get_queryset(self):
        """
        日本語ソート対応のクエリセット
        
        username でソートする場合、NULL を最後に配置
        """
        queryset = super().get_queryset()
        ordering_param = self.request.query_params.get('ordering', '')
        
        # username ソート時は NULL を最後に
        if 'username' in ordering_param:
            if ordering_param.startswith('-'):
                queryset = queryset.order_by(F('username').desc(nulls_last=True))
            else:
                queryset = queryset.order_by(F('username').asc(nulls_last=True))
        
        return queryset

    def get_serializer_class(self):
        """アクションに応じてシリアライザーを選択"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    # ==================== CRUD操作 ====================
    
    def create(self, request, *args, **kwargs):
        """
        ユーザー作成
        
        POST /api/users/
        {
            "employee_id": "E001",
            "username": "山田太郎",
            "email": "yamada@example.com",
            "password": "password123",
            "is_admin": false
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = UserService.create_user(serializer.validated_data)
        
        response_serializer = UserSerializer(user)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """
        ユーザー更新
        
        PUT/PATCH /api/users/{id}/
        {
            "username": "山田次郎",
            "email": "yamada2@example.com",
            "is_admin": true
        }
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = UserService.update_user(instance, serializer.validated_data)
            response_serializer = UserSerializer(user)
            return Response(response_serializer.data)
        except ValidationError as e:
            # DRF標準形式でエラーを返す
            return Response(
                {'detail': str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        ユーザー削除（論理削除）
        
        DELETE /api/users/{id}/
        """
        instance = self.get_object()
        
        try:
            UserService.delete_user(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response(
                {'detail': str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # ==================== カスタムアクション ====================
    
    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """
        一括削除（論理削除）
        
        POST /api/users/bulk-delete/
        {
            "ids": [1, 2, 3]
        }
        """
        user_ids = request.data.get('ids', [])
        
        if not user_ids:
            return Response(
                {'detail': '削除対象のIDを指定してください'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(user_ids, list):
            return Response(
                {'detail': 'ids は配列で指定してください'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            deleted_count = UserService.bulk_delete_users(user_ids)
            return Response({
                'message': f'{deleted_count}件のユーザーを削除しました',
                'deleted_count': deleted_count
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(
                {'detail': str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        ユーザー復元
        
        POST /api/users/{id}/restore/
        """
        try:
            user = UserService.restore_user(pk)
            serializer = UserSerializer(user)
            return Response({
                'message': 'ユーザーを復元しました',
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {'detail': '対象のユーザーが見つかりません'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'], url_path='bulk-restore')
    def bulk_restore(self, request):
        """
        一括復元
        
        POST /api/users/bulk-restore/
        {
            "ids": [1, 2, 3]
        }
        """
        user_ids = request.data.get('ids', [])
        
        if not user_ids:
            return Response(
                {'detail': '復元対象のIDを指定してください'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(user_ids, list):
            return Response(
                {'detail': 'ids は配列で指定してください'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        restored_count = UserService.bulk_restore_users(user_ids)
        return Response({
            'message': f'{restored_count}件のユーザーを復元しました',
            'restored_count': restored_count
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def deleted(self, request):
        """
        削除済みユーザー一覧
        
        GET /api/users/deleted/
        """
        deleted_users = User.all_objects.filter(deleted_at__isnull=False).order_by('-deleted_at')
        
        # フィルター・検索・ソートを適用
        deleted_users = self.filter_queryset(deleted_users)
        
        # ページネーション
        page = self.paginate_queryset(deleted_users)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserSerializer(deleted_users, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        ユーザー統計情報（高速化版）
        
        GET /api/users/stats/
        
        Returns:
        {
            "total_users": 100,
            "active_users": 95,
            "inactive_users": 5,
            "admin_users": 10,
            "deleted_users": 20
        }
        """
        # 1回のクエリで集計（高速）
        stats = User.objects.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(is_active=True)),
            inactive=Count('id', filter=Q(is_active=False)),
            admins=Count('id', filter=Q(is_admin=True, is_active=True))
        )
        
        # 削除済みユーザー数（別マネージャー使用）
        deleted_count = User.all_objects.filter(deleted_at__isnull=False).count()
        
        return Response({
            'total_users': stats['total'],
            'active_users': stats['active'],
            'inactive_users': stats['inactive'],
            'admin_users': stats['admins'],
            'deleted_users': deleted_count,
        }, status=status.HTTP_200_OK)