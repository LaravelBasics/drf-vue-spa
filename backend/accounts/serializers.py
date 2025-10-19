"""
ログイン用シリアライザー
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """ログイン入力データのバリデーション"""

    employee_id = serializers.CharField(
        max_length=50,
        required=True,
        error_messages={
            "required": _("社員番号は必須です"),
            "blank": _("社員番号は必須です"),
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
        employee_id = attrs.get("employee_id")
        password = attrs.get("password")

        if not employee_id or not password:
            raise serializers.ValidationError(_("社員番号とパスワードは必須です"))

        return attrs


class UserSerializer(serializers.ModelSerializer):
    """ユーザー情報シリアライザー（ログイン・認証用）"""

    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "employee_id",
            "username",
            "email",
            "display_name",
            "is_admin",
            "is_active",
        ]
        read_only_fields = fields
