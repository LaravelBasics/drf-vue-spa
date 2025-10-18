# backend/users/views.py
"""
ユーザー管理API（改善版）

改善ポイント:
1. バリデーションエラーの処理を統一
2. extract_error_message の使い方を明確化
3. エラーレスポンスの一貫性を確保
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from .services.user_service import UserService
from .exceptions import UserServiceException 
from .permissions import IsAdminUser
from common.mixins import ErrorResponseMixin

User = get_user_model()


class UserPagination(PageNumberPagination):
    """ユーザー一覧のページネーション設定"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(ErrorResponseMixin, viewsets.ModelViewSet):
    """ユーザー管理API"""
    
    queryset = User.objects.all()
    pagination_class = UserPagination
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_admin', 'is_active']
    search_fields = ['^employee_id', 'username']
    ordering_fields = ['id', 'employee_id', 'created_at', 'is_admin']
    ordering = ['id']
    
    def get_serializer_class(self):
        """アクションに応じてシリアライザーを切り替え"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    # ==================== CRUD ====================
    
    def create(self, request, *args, **kwargs):
        """
        ユーザー作成
        
        POST /api/users/
        """
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            user = UserService.create_user(serializer.validated_data)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            # ✅ バリデーションエラー（Django/DRF が翻訳済み）
            # detail が string の場合と dict の場合の両方に対応
            if hasattr(e, 'detail'):
                error_msg = self.extract_error_message(e.detail)
                return Response({'detail': error_msg}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """
        ユーザー詳細
        
        GET /api/users/{id}/
        """
        try:
            instance = self.get_object()
            return Response(UserSerializer(instance).data)
        except User.DoesNotExist:
            return self.error_response(
                error_code='NOT_FOUND',
                detail='ユーザーが見つかりません',
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    def update(self, request, *args, **kwargs):
        """
        ユーザー更新
        
        PUT/PATCH /api/users/{id}/
        """
        partial = kwargs.pop('partial', False)
        
        try:
            instance = self.get_object()
        except User.DoesNotExist:
            return self.error_response(
                error_code='NOT_FOUND',
                detail='ユーザーが見つかりません',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # 削除済みチェック
        if hasattr(instance, 'deleted_at') and instance.deleted_at:
            return self.error_response(
                error_code='CANNOT_UPDATE_DELETED',
                detail='削除済みユーザーは編集できません',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        try:
            serializer.is_valid(raise_exception=True)
            user = UserService.update_user(instance, serializer.validated_data)
            return Response(UserSerializer(user).data)
        
        except ValidationError as e:
            # ✅ バリデーションエラー（Django/DRF が翻訳済み）
            if hasattr(e, 'detail'):
                error_msg = self.extract_error_message(e.detail)
                return Response({'detail': error_msg}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except UserServiceException as e:
            # ✅ ビジネスロジックエラー
            return self.error_response(e.error_code, e.detail, e.status_code)
    
    def destroy(self, request, *args, **kwargs):
        """
        ユーザー削除（論理削除）
        
        DELETE /api/users/{id}/
        """
        try:
            instance = self.get_object()
        except User.DoesNotExist:
            return self.error_response(
                error_code='NOT_FOUND',
                detail='ユーザーが見つかりません',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        try:
            UserService.delete_user(instance, request_user_id=request.user.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserServiceException as e:
            return self.error_response(e.error_code, e.detail, e.status_code)
    
    # ==================== カスタムアクション ====================
    
    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """
        一括削除
        
        POST /api/users/bulk-delete/
        """
        user_ids = request.data.get('ids', [])
        
        if not user_ids:
            return self.error_response(
                error_code='VALIDATION_ERROR',
                detail='削除対象のIDを指定してください',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(user_ids, list):
            return self.error_response(
                error_code='VALIDATION_ERROR',
                detail='ids は配列で指定してください',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            deleted_count = UserService.bulk_delete_users(user_ids)
            return Response({
                'message': f'{deleted_count}件のユーザーを削除しました',
                'deleted_count': deleted_count
            })
        except UserServiceException as e:
            return self.error_response(e.error_code, e.detail, e.status_code)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        ユーザー復元
        
        POST /api/users/{id}/restore/
        """
        try:
            user = UserService.restore_user(pk)
            return Response({
                'message': 'ユーザーを復元しました',
                'user': UserSerializer(user).data
            })
        except UserServiceException as e:
            return self.error_response(e.error_code, e.detail, e.status_code)
    
    @action(detail=False, methods=['post'], url_path='bulk-restore')
    def bulk_restore(self, request):
        """
        一括復元
        
        POST /api/users/bulk-restore/
        """
        user_ids = request.data.get('ids', [])
        
        if not user_ids:
            return self.error_response(
                error_code='VALIDATION_ERROR',
                detail='復元対象のIDを指定してください',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(user_ids, list):
            return self.error_response(
                error_code='VALIDATION_ERROR',
                detail='ids は配列で指定してください',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            restored_count = UserService.bulk_restore_users(user_ids)
            return Response({
                'message': f'{restored_count}件のユーザーを復元しました',
                'restored_count': restored_count
            })
        except UserServiceException as e:
            return self.error_response(e.error_code, e.detail, e.status_code)
    
    @action(detail=False, methods=['get'])
    def deleted(self, request):
        """
        削除済みユーザー一覧
        
        GET /api/users/deleted/
        """
        deleted_users = User.all_objects.filter(deleted_at__isnull=False).order_by('-deleted_at')
        deleted_users = self.filter_queryset(deleted_users)
        
        page = self.paginate_queryset(deleted_users)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        return Response(UserSerializer(deleted_users, many=True).data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        ユーザー統計
        
        GET /api/users/stats/
        """
        stats = User.objects.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(is_active=True)),
            inactive=Count('id', filter=Q(is_active=False)),
            admins=Count('id', filter=Q(is_admin=True, is_active=True))
        )
        
        deleted_count = User.all_objects.filter(deleted_at__isnull=False).count()
        
        return Response({
            'total_users': stats['total'],
            'active_users': stats['active'],
            'inactive_users': stats['inactive'],
            'admin_users': stats['admins'],
            'deleted_users': deleted_count,
        })
    
    @action(detail=False, methods=['get'], url_path='admin-count')
    def admin_count(self, request):
        """
        アクティブな管理者数を返す
        
        GET /api/users/admin-count/
        
        レスポンス:
        {
            "count": 5,
            "can_delete": true  # 2人以上なら削除可能
        }
        """
        count = User.objects.filter(is_admin=True, is_active=True).count()
        return Response({
            'count': count,
            'can_delete': count > 1
        })


# ==================== 変更点のまとめ ====================
"""
✅ 主な変更点:

1. エラーレスポンスの統一
   - error_response() で error_code を明示的に指定
   - status_code も明示的に指定

2. ValidationError の処理
   - hasattr(e, 'detail') でチェック
   - detail がない場合も対応

3. コメントの改善
   - 各メソッドにエンドポイントを明記
   - エラーの種類を明確化

変更なし:
- ロジックは変更なし
- 動作は同じ
- エラーハンドリングをより堅牢に
"""