"""
ユーザー管理API
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
from django.http import HttpResponse
from django.utils.translation import gettext as _
import csv
from io import StringIO

from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    BulkActionSerializer,
)
from .services.user_service import UserService
from .exceptions import UserServiceException
from .permissions import IsAdminUser
from common.mixins import ErrorResponseMixin

User = get_user_model()


class UserPagination(PageNumberPagination):
    """ページネーション設定"""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UserViewSet(ErrorResponseMixin, viewsets.ModelViewSet):
    """ユーザー管理API"""

    queryset = User.objects.all()
    pagination_class = UserPagination
    permission_classes = [IsAuthenticated, IsAdminUser]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_admin", "is_active"]
    search_fields = ["^employee_id", "^username"]
    ordering_fields = ["id", "employee_id", "created_at", "is_admin"]
    ordering = ["id"]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        elif self.action in ["bulk_delete", "bulk_restore"]:
            return BulkActionSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        """ユーザー作成"""
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = UserService.create_user(serializer.validated_data)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return self.validation_error_response(e)

    def retrieve(self, request, *args, **kwargs):
        """ユーザー詳細"""
        instance = self.get_object()
        return Response(UserSerializer(instance).data)

    def update(self, request, *args, **kwargs):
        """ユーザー更新"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        if instance.deleted_at:
            return self.error_response(
                error_code="CANNOT_UPDATE_DELETED",
                detail=_("削除済みユーザーは編集できません。"),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        try:
            serializer.is_valid(raise_exception=True)
            user = UserService.update_user(instance, serializer.validated_data)
            return Response(UserSerializer(user).data)
        except ValidationError as e:
            return self.validation_error_response(e)
        except UserServiceException as e:
            return self.error_response(e.error_code, e.detail, e.status_code)

    def destroy(self, request, *args, **kwargs):
        """ユーザー削除（論理削除）"""
        instance = self.get_object()

        try:
            UserService.delete_user(instance, request_user_id=request.user.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserServiceException as e:
            return self.error_response(e.error_code, e.detail, e.status_code)

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request):
        """一括削除"""
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user_ids = serializer.validated_data["ids"]

            deleted_count = UserService.bulk_delete_users(user_ids)
            return Response(
                {
                    "message": f"{deleted_count}件のユーザーを削除しました",
                    "deleted_count": deleted_count,
                }
            )
        except ValidationError as e:
            return self.validation_error_response(e)
        except UserServiceException as e:
            return self.error_response(e.error_code, e.detail, e.status_code)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        """ユーザー復元"""
        try:
            user = UserService.restore_user(pk)
            return Response(
                {"message": "ユーザーを復元しました", "user": UserSerializer(user).data}
            )
        except UserServiceException as e:
            return self.error_response(e.error_code, e.detail, e.status_code)

    @action(detail=False, methods=["post"], url_path="bulk-restore")
    def bulk_restore(self, request):
        """一括復元"""
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user_ids = serializer.validated_data["ids"]

            restored_count = UserService.bulk_restore_users(user_ids)
            return Response(
                {
                    "message": f"{restored_count}件のユーザーを復元しました",
                    "restored_count": restored_count,
                }
            )
        except ValidationError as e:
            return self.validation_error_response(e)
        except UserServiceException as e:
            return self.error_response(e.error_code, e.detail, e.status_code)

    @action(detail=False, methods=["get"])
    def deleted(self, request):
        """削除済みユーザー一覧"""
        deleted_users = User.all_objects.filter(deleted_at__isnull=False).order_by(
            "-deleted_at"
        )
        deleted_users = self.filter_queryset(deleted_users)

        page = self.paginate_queryset(deleted_users)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response(UserSerializer(deleted_users, many=True).data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """ユーザー統計"""
        stats = User.objects.aggregate(
            total=Count("id"),
            active=Count("id", filter=Q(is_active=True)),
            inactive=Count("id", filter=Q(is_active=False)),
            admins=Count("id", filter=Q(is_admin=True, is_active=True)),
        )

        deleted_count = User.all_objects.filter(deleted_at__isnull=False).count()

        return Response(
            {
                "total_users": stats["total"],
                "active_users": stats["active"],
                "inactive_users": stats["inactive"],
                "admin_users": stats["admins"],
                "deleted_users": deleted_count,
            }
        )

    @action(detail=False, methods=["get"], url_path="admin-count")
    def admin_count(self, request):
        """管理者数取得"""
        count = User.objects.filter(is_admin=True, is_active=True).count()
        return Response({"count": count, "can_delete": count > 1})

    @action(detail=False, methods=["get"], url_path="export-csv")
    def export_csv(self, request):
        """
        CSV出力
        検索条件を反映し、100件以下のデータをCSV形式で出力
        100件超過時はエラーレスポンスを返す
        """
        # フィルタリングを適用
        queryset = self.filter_queryset(self.get_queryset())

        # 件数チェック
        count = queryset.count()
        if count > 100:
            return self.error_response(
                error_code="CSV_EXPORT_LIMIT_EXCEEDED",
                detail=_(
                    "CSV出力は100件までです。現在の検索条件では%(count)d件が該当します。"
                )
                % {"count": count},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if count == 0:
            return self.error_response(
                error_code="CSV_EXPORT_NO_DATA",
                detail=_("出力対象のデータがありません。"),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # ソートを適用
        ALLOWED_ORDERING = [
            "id",
            "-id",
            "employee_id",
            "-employee_id",
            "username",
            "-username",
            "email",
            "-email",
            "created_at",
            "-created_at",
        ]
        ordering = request.query_params.get("ordering", "id")
        if ordering not in ALLOWED_ORDERING:
            ordering = "id"

        queryset = queryset.order_by(ordering)

        # CSV生成
        output = StringIO()
        writer = csv.writer(output)

        # ヘッダー行
        writer.writerow(
            [
                "ID",
                _("社員番号"),
                _("ユーザー名"),
                _("メールアドレス"),
                _("管理者"),
                _("アクティブ"),
                _("作成日時"),
            ]
        )

        # データ行
        for user in queryset:
            writer.writerow(
                [
                    user.id,
                    user.employee_id,
                    user.username or "",
                    user.email or "",
                    "○" if user.is_admin else "",
                    "○" if user.is_active else "",
                    user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

        # レスポンス生成
        response = HttpResponse(
            output.getvalue().encode("utf-8-sig"),  # BOM付きUTF-8でExcel対応
            content_type="text/csv; charset=utf-8-sig",
        )
        response["Content-Disposition"] = 'attachment; filename="users.csv"'

        return response
