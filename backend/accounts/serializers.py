# accounts/serializers.py
"""
グループ認証対応 ログイン用シリアライザー
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from common.models import MUserGroup, MGroup

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """ログイン入力データのバリデーション"""

    group_id = serializers.CharField(
        max_length=50,
        required=True,
        error_messages={
            "required": _("グループIDは必須です"),
            "blank": _("グループIDは必須です"),
        },
    )

    user_id = serializers.CharField(
        max_length=50,
        required=True,
        error_messages={
            "required": _("ユーザーIDは必須です"),
            "blank": _("ユーザーIDは必須です"),
        },
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            "required": _("パスワードは必須です"),
            "blank": _("パスワードは必須です"),
        },
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        """空白入力の防止"""
        group_id = attrs.get("group_id")
        user_id = attrs.get("user_id")
        password = attrs.get("password")

        if not group_id or not user_id or not password:
            raise serializers.ValidationError(
                _("グループID、ユーザーID、パスワードは必須です")
            )

        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    ユーザー情報シリアライザー（ログイン・認証用）

    is_admin: is_superuser または is_staff の論理和（プロパティから取得）
    current_group: セッションから現在のグループ情報を取得
    """

    current_group = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "is_active",
            "is_superuser",  # ✅ PostgreSQLフィールド
            "is_staff",  # ✅ PostgreSQLフィールド
            "is_admin",  # ✅ 後方互換性のための計算フィールド
            "current_group",
        ]
        read_only_fields = fields

    def get_is_admin(self, obj):
        """
        管理者権限チェック

        is_superuser=True または is_staff=True なら管理者とみなす
        （models.pyの is_admin プロパティと同じロジック）

        Returns:
            bool: 管理者ならTrue
        """
        return bool(obj.is_superuser or obj.is_staff)

    def get_current_group(self, obj):
        """
        セッションから現在のグループ情報を取得

        Returns:
            dict: {group_id: str, group_name: str} or None
        """
        request = self.context.get("request")

        if not request or not hasattr(request, "session"):
            return None

        group_id = request.session.get("current_group_id")
        if not group_id:
            return None

        try:
            # ユーザー所属確認
            MUserGroup.objects.get(
                user_id=obj.user_id,
                group_id=group_id,
                is_active=True,
            )

            # グループ情報取得
            group_obj = MGroup.objects.get(
                group_id=group_id,
                is_active=True,
            )

            return {
                "group_id": group_obj.group_id,
                "group_name": group_obj.group_name,
            }

        except (MUserGroup.DoesNotExist, MGroup.DoesNotExist):
            return None


class GroupSerializer(serializers.Serializer):
    """グループ情報シリアライザ（ログイン画面用）"""

    group_id = serializers.CharField()
    group_name = serializers.CharField()
