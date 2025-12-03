"""
グループ認証対応 ログイン用シリアライザー
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from users.models import UserGroup

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

    current_group: セッションから現在のグループ情報を取得して返す
    """

    current_group = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "email",
            "is_admin",
            "is_active",
            "current_group",  # ← 追加
        ]
        read_only_fields = fields

    def get_current_group(self, obj):
        """
        セッションから現在のグループ情報を取得

        Returns:
            dict: {group_id: str, group_name: str} or None
        """
        request = self.context.get("request")

        # requestがない、またはsessionがない場合はNone
        if not request or not hasattr(request, "session"):
            return None

        # セッションからグループIDを取得
        group_id = request.session.get("current_group_id")

        if not group_id:
            return None

        try:
            # ユーザーが所属しているアクティブなグループか確認
            user_group = UserGroup.objects.select_related("group").get(
                user=obj,
                group_id=group_id,
                is_active=True,
                group__is_active=True,
            )

            return {
                "group_id": user_group.group.group_id,
                "group_name": user_group.group.group_name,
            }
        except UserGroup.DoesNotExist:
            # グループが見つからない場合はNoneを返す
            return None


class GroupSerializer(serializers.Serializer):
    """グループ情報シリアライザ（ログイン画面用）"""

    group_id = serializers.CharField()
    group_name = serializers.CharField()
