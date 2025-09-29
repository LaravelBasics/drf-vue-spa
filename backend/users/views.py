from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """ユーザー管理ViewSet"""
    
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    
    # 検索フィールド（前方一致）
    search_fields = ['^username']  # ^ は前方一致
    
    # フィルタリング可能フィールド
    filterset_fields = ['is_admin', 'is_active']
    
    # ソート可能フィールド
    ordering_fields = ['username', 'employee_id', 'created_at', 'is_admin']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """アクションに応じてシリアライザーを選択"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """ユーザー削除（管理者最低1人チェック）"""
        instance = self.get_object()
        
        # 削除対象が管理者の場合、他にアクティブな管理者がいるかチェック
        if instance.is_admin:
            active_admin_count = User.objects.filter(
                is_admin=True, 
                is_active=True
            ).exclude(id=instance.id).count()
            
            if active_admin_count == 0:
                return Response(
                    {
                        'error': '管理者は最低1人必要です。最後の管理者を削除することはできません。'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """ユーザー統計情報"""
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        admin_users = User.objects.filter(is_admin=True, is_active=True).count()
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users,
        })