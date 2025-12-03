"""
ログイン用シリアライザー
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

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
    """ユーザー情報シリアライザー（ログイン・認証用）"""

    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "email",
            "is_admin",
            "is_active",
        ]
        read_only_fields = fields


class GroupSerializer(serializers.Serializer):
    """グループ情報シリアライザ"""

    group_id = serializers.CharField()
    group_name = serializers.CharField()
