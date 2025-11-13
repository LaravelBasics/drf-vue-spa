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
from django.http import HttpResponse
from django.utils.translation import gettext as _
from datetime import datetime
import re
import csv
from io import StringIO

from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)
from .services.user_service import UserService
from .exceptions import (
    UserServiceException,
    UserNotFoundError,
    DeletedUserAccessError,
)
from .permissions import IsAdminUser
from common.response_utils import extract_validation_error

User = get_user_model()


class UserPagination(PageNumberPagination):
    """ページネーション設定"""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
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

    def get_queryset(self):
        """
        アクションに応じてクエリセットを動的に変更
        - retrieve: 削除済みも含める（明確なエラーメッセージのため）
        - その他: 削除済みを除外
        """
        queryset = super().get_queryset()

        if self.action == "retrieve":
            # all_objectsマネージャーを使って削除済みも取得
            return User.all_objects.all()

        # list などは削除済みを除外
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        """ユーザー作成"""
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = UserService.create_user(serializer.validated_data)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            error_msg = extract_validation_error(e)
            return Response({"detail": error_msg}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        ユーザー詳細取得
        削除済みユーザーへのアクセスを防止（ブラウザback対策）
        """
        instance = self.get_object()

        # 削除済みユーザーのチェック
        if instance.deleted_at:
            raise DeletedUserAccessError()

        return Response(UserSerializer(instance).data)

    def update(self, request, *args, **kwargs):
        """
        ユーザー更新

        Note:
            同時操作対応: all_objectsで取得して削除済みを明示的にチェック
        """
        partial = kwargs.pop("partial", False)

        # all_objectsを使って削除済みも含めて取得（同時削除対策）
        try:
            instance = User.all_objects.get(pk=self.kwargs["pk"])
        except User.DoesNotExist:
            raise UserNotFoundError()

        # 削除済みチェック（別タブで削除された場合）
        if instance.deleted_at:
            raise DeletedUserAccessError()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        try:
            serializer.is_valid(raise_exception=True)
            user = UserService.update_user(instance, serializer.validated_data)
            return Response(UserSerializer(user).data)
        except ValidationError as e:
            error_msg = extract_validation_error(e)
            return Response({"detail": error_msg}, status=status.HTTP_400_BAD_REQUEST)
        except UserServiceException as e:
            return Response({"detail": e.detail}, status=e.status_code)

    def destroy(self, request, *args, **kwargs):
        """
        ユーザー削除（論理削除）

        Note:
            同時操作対応: all_objectsで取得して削除済みを明示的にチェック
        """
        # all_objectsを使って削除済みも含めて取得（同時削除対策）
        try:
            instance = User.all_objects.get(pk=self.kwargs["pk"])
        except User.DoesNotExist:
            raise UserNotFoundError()

        # 削除済みチェック（別タブで削除された場合）
        if instance.deleted_at:
            raise DeletedUserAccessError()

        try:
            UserService.delete_user(instance, request_user_id=request.user.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserServiceException as e:
            return Response({"detail": e.detail}, status=e.status_code)

    @action(detail=False, methods=["get"], url_path="admin-count")
    def admin_count(self, request):
        """管理者数取得"""
        count = User.objects.filter(is_admin=True, is_active=True).count()
        return Response({"count": count, "can_delete": count > 1})

    @action(detail=False, methods=["get"], url_path="export-csv")
    def export_csv(self, request):
        """
        CSV出力
        検索条件を反映し、1100件以下のデータをCSV形式で出力
        1100件超過時はエラーレスポンスを返す
        """
        # フィルタリングを適用
        queryset = self.filter_queryset(self.get_queryset())

        # 件数チェック
        count = queryset.count()
        if count > 1100:
            return Response(
                {
                    "detail": _(
                        "CSV出力は1100件までです。現在の検索条件では%(count)d件が該当します。"
                    )
                    % {"count": count}
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if count == 0:
            return Response(
                {"detail": _("出力対象のデータがありません。")},
                status=status.HTTP_400_BAD_REQUEST,
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
                    "○" if user.is_admin else "",
                    "○" if user.is_active else "",
                    user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

        # ファイル名生成
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        # オプション：検索条件をファイル名に含める
        search_term = request.query_params.get("search", "")
        if search_term:
            # サニタイズ
            safe_search = re.sub(r"[^\w\s-]", "", search_term)[:20]
            filename = f"users_{safe_search}_{timestamp}.csv"
        else:
            filename = f"users_{timestamp}.csv"

        # レスポンス生成
        response = HttpResponse(
            output.getvalue().encode("utf-8-sig"),  # BOM付きUTF-8でExcel対応
            content_type="text/csv; charset=utf-8-sig",
        )

        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response
