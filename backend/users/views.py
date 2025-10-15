# backend/users/views.py
"""
ユーザー管理API

このファイルの役割:
- ユーザーの CRUD（作成・読取・更新・削除）
- 一括操作（一括削除・一括復元）
- 統計情報の取得
- 削除済みユーザーの管理

ViewSet とは:
- 複数のアクション（list, create, retrieve, update, destroy）をまとめたもの
- REST API の標準的な操作を自動的に実装してくれる
"""

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


# ==================== ページネーション設定 ====================

class UserPagination(PageNumberPagination):
    """
    ユーザー一覧のページ分割設定
    
    ページネーションとは:
    - 大量のデータを小分けにして返す仕組み
    - 例: 100件のユーザーを10件ずつ10ページに分ける
    
    設定内容:
    - page_size: 1ページあたり10件
    - page_size_query_param: クエリで変更可能（?page_size=20）
    - max_page_size: 最大100件まで
    """
    page_size = 10                      # デフォルトのページサイズ
    page_size_query_param = 'page_size' # ?page_size=20 で変更可能
    max_page_size = 100                 # 最大100件まで


# ==================== メインのViewSet ====================

class UserViewSet(ErrorResponseMixin, viewsets.ModelViewSet):
    """
    ユーザー管理API
    
    継承クラス:
    - ErrorResponseMixin: エラーレスポンスの統一形式
    - ModelViewSet: CRUD操作の自動実装
    
    自動実装されるアクション:
    - list: GET /api/users/ → ユーザー一覧
    - create: POST /api/users/ → ユーザー作成
    - retrieve: GET /api/users/{id}/ → ユーザー詳細
    - update: PUT /api/users/{id}/ → ユーザー更新
    - partial_update: PATCH /api/users/{id}/ → 部分更新
    - destroy: DELETE /api/users/{id}/ → ユーザー削除
    
    追加のカスタムアクション:
    - bulk_delete: 一括削除
    - restore: 復元
    - bulk_restore: 一括復元
    - deleted: 削除済み一覧
    - stats: 統計情報
    """
    
    # ==================== 基本設定 ====================
    
    # 取得するデータ（削除済みは除外）
    queryset = User.objects.all()
    
    # ページネーション
    pagination_class = UserPagination
    
    # 権限（ログイン済み かつ 管理者のみ）
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    # ==================== フィルター・検索・並び替え ====================
    
    # フィルターバックエンド（3種類を有効化）
    filter_backends = [
        DjangoFilterBackend,    # フィルター（?is_admin=true）
        filters.SearchFilter,   # 検索（?search=山田）
        filters.OrderingFilter  # 並び替え（?ordering=-created_at）
    ]
    
    # フィルター可能なフィールド
    # 使い方: ?is_admin=true&is_active=false
    filterset_fields = ['is_admin', 'is_active']
    
    # 検索対象フィールド
    # ^ = 前方一致（employee_id が "EMP" で始まる）
    # 使い方: ?search=山田
    search_fields = ['^employee_id', 'username']
    
    # 並び替え可能なフィールド
    # 使い方: ?ordering=-created_at （新しい順）
    ordering_fields = ['id', 'employee_id', 'created_at', 'is_admin']
    
    # デフォルトの並び順
    ordering = ['id']
    
    # ==================== カスタムメソッド ====================
    
    # def get_queryset(self):
    #     """
    #     取得するデータをカスタマイズ
        
    #     日本語ソート対応:
    #     - username で並び替える時、NULL値を最後にする
    #     - 例: ?ordering=username → あ、い、う...、NULL
    #     """
    #     queryset = super().get_queryset()
    #     ordering_param = self.request.query_params.get('ordering', '')
        
    #     username での並び替え時の特別処理
    #     if 'username' in ordering_param:
    #         if ordering_param.startswith('-'):
    #             # 降順（新→古）
    #             queryset = queryset.order_by(F('username').desc(nulls_last=True))
    #         else:
    #             # 昇順（古→新）
    #             queryset = queryset.order_by(F('username').asc(nulls_last=True))
        
    #     return queryset

    def get_serializer_class(self):
        """
        アクションに応じてシリアライザーを切り替え
        
        - 作成時: UserCreateSerializer（パスワード必須）
        - 更新時: UserUpdateSerializer（パスワード任意）
        - その他: UserSerializer（表示用）
        """
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    # ==================== CRUD操作（基本） ====================
    
    def create(self, request, *args, **kwargs):
        """
        ユーザー作成
        
        エンドポイント: POST /api/users/
        
        リクエストボディ:
        {
            "employee_id": "EMP001",
            "username": "山田太郎",
            "email": "yamada@example.com",
            "password": "password123",
            "is_admin": false
        }
        
        レスポンス:
        - 成功: 201 Created + ユーザー情報
        - 失敗: 400 Bad Request + エラーメッセージ
        """
        # シリアライザーでバリデーション
        serializer = self.get_serializer(data=request.data)
        
        try:
            # バリデーション実行
            serializer.is_valid(raise_exception=True)
            
            # UserService でユーザー作成
            user = UserService.create_user(serializer.validated_data)
            
            # 成功レスポンス
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            # ⭐ ValidationError から error_code を抽出
            error_code = self._extract_error_code(e)

            # バリデーションエラー
            error_msg = self.extract_error_message(e.detail)
            return self.error_response(error_code, error_msg)
        

    def _extract_error_code(self, validation_error):
        """
        ValidationError から error_code を抽出
    
        DRF の ValidationError は以下の形式:
        {
            'employee_id': [
                ErrorDetail(string='...', code='EMPLOYEE_ID_EXISTS')
            ]
        }
        """
        detail = validation_error.detail
    
        # フィールドごとのエラー（dict）
        if isinstance(detail, dict):
            for field_errors in detail.values():
                if isinstance(field_errors, list) and len(field_errors) > 0:
                    error = field_errors[0]
                    if hasattr(error, 'code') and error.code != 'invalid':
                        return error.code
    
        # リストのエラー
        elif isinstance(detail, list) and len(detail) > 0:
            error = detail[0]
            if hasattr(error, 'code') and error.code != 'invalid':
                return error.code
        
        # デフォルト
        return 'VALIDATION_ERROR'
    
    def retrieve(self, request, *args, **kwargs):
        """
        ユーザー詳細
        
        エンドポイント: GET /api/users/{id}/
        
        レスポンス:
        - 成功: 200 OK + ユーザー情報
        - 失敗: 404 Not Found
        """
        try:
            # IDでユーザーを取得
            instance = self.get_object()
            return Response(UserSerializer(instance).data)
        
        except User.DoesNotExist:
            return self.error_response('NOT_FOUND', 'ユーザーが見つかりません', status.HTTP_404_NOT_FOUND)
    
    def update(self, request, *args, **kwargs):
        """
        ユーザー更新
        
        エンドポイント:
        - PUT /api/users/{id}/ → 全フィールド必須
        - PATCH /api/users/{id}/ → 一部フィールドのみでOK
        
        リクエストボディ:
        {
            "employee_id": "EMP001",
            "username": "山田太郎",
            "email": "yamada@example.com",
            "password": "newpassword123",  // 任意
            "is_admin": false,
            "is_active": true
        }
        
        レスポンス:
        - 成功: 200 OK + 更新されたユーザー情報
        - 失敗: 400/404
        """
        # PATCH（部分更新）かどうか
        partial = kwargs.pop('partial', False)
        
        try:
            # 更新対象のユーザーを取得
            instance = self.get_object()
        except User.DoesNotExist:
            return self.error_response('NOT_FOUND', 'ユーザーが見つかりません', status.HTTP_404_NOT_FOUND)
        
        # 削除済みユーザーは更新不可
        if hasattr(instance, 'deleted_at') and instance.deleted_at:
            return self.error_response('CANNOT_UPDATE_DELETED', '削除済みユーザーは編集できません')
        
        # シリアライザーでバリデーション
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        try:
            serializer.is_valid(raise_exception=True)
            
            # UserService でユーザー更新
            user = UserService.update_user(instance, serializer.validated_data)
            
            return Response(UserSerializer(user).data)
        
        except ValidationError as e:
            error_msg = self.extract_error_message(e.detail)
            return self.error_response('VALIDATION_ERROR', error_msg)
        
        except UserServiceException as e:
            # 業務ルールエラー（最後の管理者など）
            return self.error_response(e.error_code, e.detail, e.status_code)
    
    def destroy(self, request, *args, **kwargs):
        """
        ユーザー削除（論理削除）
        
        エンドポイント: DELETE /api/users/{id}/
        
        論理削除とは:
        - データベースから物理的に削除しない
        - deleted_at に日時を記録して「削除済み」とマーク
        - 後で復元できる
        
        レスポンス:
        - 成功: 204 No Content
        - 失敗: 400/404
        """
        try:
            # 削除対象のユーザーを取得
            instance = self.get_object()
        except User.DoesNotExist:
            return self.error_response('NOT_FOUND', 'ユーザーが見つかりません', status.HTTP_404_NOT_FOUND)
        
        try:
            # UserService で論理削除
            # request.user.id = ログイン中のユーザーID（自分自身削除チェック用）
            UserService.delete_user(instance, request_user_id=request.user.id)
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except UserServiceException as e:
            # 業務ルールエラー（自分自身削除、最後の管理者など）
            return self.error_response(e.error_code, e.detail, e.status_code)
    
    # ==================== カスタムアクション ====================
    
    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """
        一括削除（論理削除）
        
        エンドポイント: POST /api/users/bulk-delete/
        
        リクエストボディ:
        {
            "ids": [1, 2, 3, 4, 5]
        }
        
        レスポンス:
        {
            "message": "5件のユーザーを削除しました",
            "deleted_count": 5
        }
        
        注意:
        - detail=False → /api/users/bulk-delete/
        - detail=True → /api/users/{id}/bulk-delete/ （使わない）
        """
        # リクエストボディから ids を取得
        user_ids = request.data.get('ids', [])
        
        # バリデーション
        if not user_ids:
            return self.error_response('VALIDATION_ERROR', '削除対象のIDを指定してください')
        
        if not isinstance(user_ids, list):
            return self.error_response('VALIDATION_ERROR', 'ids は配列で指定してください')
        
        try:
            # UserService で一括削除
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
        
        エンドポイント: POST /api/users/{id}/restore/
        
        削除済みユーザーを復元する
        
        レスポンス:
        {
            "message": "ユーザーを復元しました",
            "user": { ユーザー情報 }
        }
        
        注意:
        - detail=True → /api/users/{id}/restore/
        - pk = URL の {id} 部分
        """
        try:
            # UserService で復元
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
        
        エンドポイント: POST /api/users/bulk-restore/
        
        リクエストボディ:
        {
            "ids": [1, 2, 3]
        }
        
        レスポンス:
        {
            "message": "3件のユーザーを復元しました",
            "restored_count": 3
        }
        """
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
        """
        削除済みユーザー一覧
        
        エンドポイント: GET /api/users/deleted/
        
        削除済み（deleted_at が NULL でない）ユーザーのみ取得
        
        レスポンス: ページネーション付きユーザー一覧
        """
        # all_objects = 削除済みも含む全件取得
        deleted_users = User.all_objects.filter(deleted_at__isnull=False).order_by('-deleted_at')
        
        # フィルター・検索を適用
        deleted_users = self.filter_queryset(deleted_users)
        
        # ページネーション
        page = self.paginate_queryset(deleted_users)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # ページネーションなしの場合
        return Response(UserSerializer(deleted_users, many=True).data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        ユーザー統計情報
        
        エンドポイント: GET /api/users/stats/
        
        レスポンス:
        {
            "total_users": 100,      // 全ユーザー数
            "active_users": 80,      // アクティブユーザー数
            "inactive_users": 20,    // 無効化ユーザー数
            "admin_users": 5,        // 管理者数
            "deleted_users": 10      // 削除済みユーザー数
        }
        
        集計の仕組み:
        - Count('id'): IDをカウント
        - filter=Q(...): 条件付きカウント
        """
        # aggregate = 集計関数
        stats = User.objects.aggregate(
            total=Count('id'),  # 全件
            active=Count('id', filter=Q(is_active=True)),  # アクティブのみ
            inactive=Count('id', filter=Q(is_active=False)),  # 無効のみ
            admins=Count('id', filter=Q(is_admin=True, is_active=True))  # 管理者のみ
        )
        
        # 削除済みは別途カウント（all_objects で取得）
        deleted_count = User.all_objects.filter(deleted_at__isnull=False).count()
        
        return Response({
            'total_users': stats['total'],
            'active_users': stats['active'],
            'inactive_users': stats['inactive'],
            'admin_users': stats['admins'],
            'deleted_users': deleted_count,
        })


# ==================== API使用例 ====================
"""
1. ユーザー一覧取得
GET /api/users/
GET /api/users/?page=2
GET /api/users/?page_size=20
GET /api/users/?is_admin=true
GET /api/users/?search=山田
GET /api/users/?ordering=-created_at

2. ユーザー作成
POST /api/users/
Body: {"employee_id": "EMP001", "username": "山田太郎", ...}

3. ユーザー詳細
GET /api/users/1/

4. ユーザー更新
PUT /api/users/1/
PATCH /api/users/1/

5. ユーザー削除
DELETE /api/users/1/

6. 一括削除
POST /api/users/bulk-delete/
Body: {"ids": [1, 2, 3]}

7. 復元
POST /api/users/1/restore/

8. 一括復元
POST /api/users/bulk-restore/
Body: {"ids": [1, 2, 3]}

9. 削除済み一覧
GET /api/users/deleted/

10. 統計情報
GET /api/users/stats/
"""