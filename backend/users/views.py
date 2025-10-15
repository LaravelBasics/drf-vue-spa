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
    ordering_fields = ['id', 'employee_id', 'username', 'created_at', 'is_admin']
    ordering = ['id']
    
    def get_queryset(self):
        """日本語ソート対応"""
        queryset = super().get_queryset()
        ordering_param = self.request.query_params.get('ordering', '')
        
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
    
    # ==================== CRUD ====================
    
    def create(self, request, *args, **kwargs):
        """ユーザー作成"""
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            user = UserService.create_user(serializer.validated_data)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            error_msg = self.extract_error_message(e.detail)
            return self.error_response('VALIDATION_ERROR', error_msg)
    
    def retrieve(self, request, *args, **kwargs):
        """ユーザー詳細"""
        try:
            instance = self.get_object()
            return Response(UserSerializer(instance).data)
        except User.DoesNotExist:
            return self.error_response('NOT_FOUND', 'ユーザーが見つかりません', status.HTTP_404_NOT_FOUND)
    
    def update(self, request, *args, **kwargs):
        """ユーザー更新"""
        partial = kwargs.pop('partial', False)
        
        try:
            instance = self.get_object()
        except User.DoesNotExist:
            return self.error_response('NOT_FOUND', 'ユーザーが見つかりません', status.HTTP_404_NOT_FOUND)
        
        if hasattr(instance, 'deleted_at') and instance.deleted_at:
            return self.error_response('CANNOT_UPDATE_DELETED', '削除済みユーザーは編集できません')
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        try:
            serializer.is_valid(raise_exception=True)
            user = UserService.update_user(instance, serializer.validated_data)
            return Response(UserSerializer(user).data)
        except ValidationError as e:
            error_msg = self.extract_error_message(e.detail)
            return self.error_response('VALIDATION_ERROR', error_msg)
        except UserServiceException as e:
            return self.error_response(e.error_code, e.detail, e.status_code)
    
    def destroy(self, request, *args, **kwargs):
        """ユーザー削除（論理削除）"""
        try:
            instance = self.get_object()
        except User.DoesNotExist:
            return self.error_response('NOT_FOUND', 'ユーザーが見つかりません', status.HTTP_404_NOT_FOUND)
        
        try:
            UserService.delete_user(instance, request_user_id=request.user.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserServiceException as e:
            return self.error_response(e.error_code, e.detail, e.status_code)
    
    # ==================== カスタムアクション ====================
    
    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """一括削除（論理削除）"""
        user_ids = request.data.get('ids', [])
        
        if not user_ids:
            return self.error_response('VALIDATION_ERROR', '削除対象のIDを指定してください')
        
        if not isinstance(user_ids, list):
            return self.error_response('VALIDATION_ERROR', 'ids は配列で指定してください')
        
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
        """ユーザー復元"""
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
        """一括復元"""
        user_ids = request.data.get('ids', [])
        
        if not user_ids:
            return self.error_response('VALIDATION_ERROR', '復元対象のIDを指定してください')
        
        if not isinstance(user_ids, list):
            return self.error_response('VALIDATION_ERROR', 'ids は配列で指定してください')
        
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
        """削除済みユーザー一覧"""
        deleted_users = User.all_objects.filter(deleted_at__isnull=False).order_by('-deleted_at')
        deleted_users = self.filter_queryset(deleted_users)
        
        page = self.paginate_queryset(deleted_users)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        return Response(UserSerializer(deleted_users, many=True).data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """ユーザー統計"""
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