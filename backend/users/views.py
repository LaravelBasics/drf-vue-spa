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
        
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            # ⭐ バリデーションエラーをエラーコード化
            return self._handle_validation_error(e)
        
        user = UserService.create_user(serializer.validated_data)
        
        response_serializer = UserSerializer(user)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, *args, **kwargs):
        """ユーザー詳細取得（エラーコード対応）"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {
                    'error_code': 'NOT_FOUND',
                    'detail': 'ユーザーが見つかりません'
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    def update(self, request, *args, **kwargs):
        """
        ユーザー更新
        
        PUT/PATCH /api/users/{id}/
        {
            "username": "山田次郎",
            "email": "yamada2@example.com",
            "is_admin": true,
            "is_active": false
        }
        """
        partial = kwargs.pop('partial', False)
        
        try:
            instance = self.get_object()
        except User.DoesNotExist:
            return Response(
                {
                    'error_code': 'NOT_FOUND',
                    'detail': 'ユーザーが見つかりません'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 削除済みユーザーチェック
        if hasattr(instance, 'deleted_at') and instance.deleted_at:
            return Response(
                {
                    'error_code': 'CANNOT_UPDATE_DELETED',
                    'detail': '削除済みユーザーは編集できません'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return self._handle_validation_error(e)
        
        try:
            # ⭐ 最後の管理者のチェック
            validated_data = serializer.validated_data
            
            # 現在、管理者かつアクティブな場合
            if instance.is_admin and instance.is_active:
                # 他の管理者（アクティブ）がいるかチェック
                other_admins = User.objects.filter(
                    is_admin=True,
                    is_active=True
                ).exclude(id=instance.id).count()
                
                if other_admins == 0:
                    # ケース1: アカウント無効化しようとしている
                    if 'is_active' in validated_data and not validated_data['is_active']:
                        return Response(
                            {
                                'error_code': 'LAST_ADMIN_CANNOT_DEACTIVATE',
                                'detail': '最後の管理者はアカウントを無効化できません'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # ケース2: 管理者権限を外そうとしている
                    if 'is_admin' in validated_data and not validated_data['is_admin']:
                        return Response(
                            {
                                'error_code': 'LAST_ADMIN_CANNOT_REMOVE',
                                'detail': '最後の管理者は変更できません'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
            
            user = UserService.update_user(instance, validated_data)
            response_serializer = UserSerializer(user)
            return Response(response_serializer.data)
        except ValidationError as e:
            return Response(
                {
                    'error_code': 'VALIDATION_ERROR',
                    'detail': str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        ユーザー削除（論理削除）
        
        DELETE /api/users/{id}/
        """
        try:
            instance = self.get_object()
        except User.DoesNotExist:
            return Response(
                {
                    'error_code': 'NOT_FOUND',
                    'detail': 'ユーザーが見つかりません'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 自分自身の削除を防止
        if instance.id == request.user.id:
            return Response(
                {
                    'error_code': 'CANNOT_DELETE_SELF',
                    'detail': '自分自身を削除することはできません'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            UserService.delete_user(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            # 最後の管理者削除エラー
            error_message = str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)
            
            error_code = 'VALIDATION_ERROR'
            if '最後の管理者' in error_message:
                error_code = 'LAST_ADMIN'
            
            return Response(
                {
                    'error_code': error_code,
                    'detail': error_message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # ==================== ヘルパーメソッド ====================
    
    def _handle_validation_error(self, validation_error):
        """
        DRF ValidationError をエラーコード付きレスポンスに変換
        
        Args:
            validation_error: rest_framework.exceptions.ValidationError
        
        Returns:
            Response: エラーコード付きレスポンス
        """
        error_detail = validation_error.detail
        
        # フィールド別エラーの場合
        if isinstance(error_detail, dict):
            # 最初のフィールドエラーを取得
            first_field = next(iter(error_detail))
            first_error = error_detail[first_field]
            
            if isinstance(first_error, list):
                error_message = str(first_error[0])
            else:
                error_message = str(first_error)
            
            # エラーコードの判定
            error_code = self._detect_error_code(first_field, error_message)
            
            return Response(
                {
                    'error_code': error_code,
                    'detail': error_message,
                    'field': first_field
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # non_field_errors の場合
        if isinstance(error_detail, list):
            error_message = str(error_detail[0])
        else:
            error_message = str(error_detail)
        
        return Response(
            {
                'error_code': 'VALIDATION_ERROR',
                'detail': error_message
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def _detect_error_code(self, field_name, error_message):
        """エラーメッセージからエラーコードを判定"""
        error_message_lower = error_message.lower()
        
        # 社員番号関連
        if field_name == 'employee_id':
            if '既に使用' in error_message or 'already exists' in error_message_lower:
                return 'EMPLOYEE_ID_EXISTS'
            if '必須' in error_message or 'required' in error_message_lower:
                return 'EMPLOYEE_ID_REQUIRED'
        
        # ユーザー名関連
        if field_name == 'username':
            if '必須' in error_message or 'required' in error_message_lower:
                return 'USERNAME_REQUIRED'
        
        # パスワード関連
        if field_name == 'password':
            if '8文字' in error_message or 'at least 8' in error_message_lower:
                return 'PASSWORD_TOO_SHORT'
        
        # メールアドレス関連
        if field_name == 'email':
            if 'メールアドレス' in error_message or 'email' in error_message_lower:
                return 'INVALID_EMAIL'
        
        return 'VALIDATION_ERROR'

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
                {
                    'error_code': 'VALIDATION_ERROR',
                    'detail': '削除対象のIDを指定してください'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(user_ids, list):
            return Response(
                {
                    'error_code': 'VALIDATION_ERROR',
                    'detail': 'ids は配列で指定してください'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            deleted_count = UserService.bulk_delete_users(user_ids)
            return Response({
                'message': f'{deleted_count}件のユーザーを削除しました',
                'deleted_count': deleted_count
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            error_message = str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)
            
            # エラーコード判定
            error_code = 'VALIDATION_ERROR'
            if '最後の管理者' in error_message:
                error_code = 'LAST_ADMIN'
            elif '自分自身' in error_message:
                error_code = 'CANNOT_DELETE_SELF'
            
            return Response(
                {
                    'error_code': error_code,
                    'detail': error_message
                },
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
                {
                    'error_code': 'NOT_FOUND',
                    'detail': '対象のユーザーが見つかりません'
                },
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
                {
                    'error_code': 'VALIDATION_ERROR',
                    'detail': '復元対象のIDを指定してください'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(user_ids, list):
            return Response(
                {
                    'error_code': 'VALIDATION_ERROR',
                    'detail': 'ids は配列で指定してください'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            restored_count = UserService.bulk_restore_users(user_ids)
            return Response({
                'message': f'{restored_count}件のユーザーを復元しました',
                'restored_count': restored_count
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            error_message = str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)
            
            return Response(
                {
                    'error_code': 'VALIDATION_ERROR',
                    'detail': error_message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
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