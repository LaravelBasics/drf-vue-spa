"""
ユーザー管理シリアライザー
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


EMPLOYEE_ID_UNIQUE_VALIDATOR = UniqueValidator(
    queryset=User.objects.all(), message=_("社員番号は既に使用されています")
)


class UserSerializer(serializers.ModelSerializer):
    """ユーザー情報取得用"""

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
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserCreateSerializer(serializers.ModelSerializer):
    """ユーザー作成用"""

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        min_length=8,
        max_length=128,
        error_messages={
            "min_length": _("パスワードは8文字以上で入力してください"),
            "max_length": _("パスワードは128文字以内で入力してください"),
            "required": _("パスワードは必須です"),
        },
    )

    employee_id = serializers.CharField(
        required=True,
        max_length=50,
        validators=[EMPLOYEE_ID_UNIQUE_VALIDATOR],
        error_messages={
            "required": _("社員番号は必須です"),
            "blank": _("社員番号は必須です"),
            "max_length": _("社員番号は50文字以内で入力してください"),
        },
    )

    username = serializers.CharField(
        required=True,
        error_messages={
            "required": _("ユーザー名は必須です"),
            "blank": _("ユーザー名は必須です"),
        },
    )

    class Meta:
        model = User
        fields = [
            "employee_id",
            "username",
            "email",
            "password",
            "is_admin",
        ]

    def validate_employee_id(self, value):
        """値の正規化（空白削除）"""
        return value.strip() if value else value

    def validate_email(self, value):
        """メールアドレス正規化（小文字変換）"""
        return value.strip().lower() if value else None


class UserUpdateSerializer(serializers.ModelSerializer):
    """ユーザー更新用"""

    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={"input_type": "password"},
        min_length=8,
        max_length=128,
        error_messages={
            "min_length": _("パスワードは8文字以上で入力してください"),
            "max_length": _("パスワードは128文字以内で入力してください"),
        },
    )

    employee_id = serializers.CharField(
        required=True,
        max_length=50,
        validators=[EMPLOYEE_ID_UNIQUE_VALIDATOR],
        error_messages={
            "required": _("社員番号は必須です"),
            "blank": _("社員番号は必須です"),
            "max_length": _("社員番号は50文字以内で入力してください"),
        },
    )

    username = serializers.CharField(
        required=True,
        error_messages={
            "required": _("ユーザー名は必須です"),
            "blank": _("ユーザー名は必須です"),
        },
    )

    class Meta:
        model = User
        fields = [
            "employee_id",
            "username",
            "email",
            "password",
            "is_admin",
            "is_active",
        ]

    def validate_employee_id(self, value):
        """値の正規化（空白削除）"""
        return value.strip() if value else value

    def validate_email(self, value):
        """メールアドレス正規化（小文字変換）"""
        return value.strip().lower() if value else None

    def validate_password(self, value):
        """パスワード検証（空白のみは変更なし）"""
        return value.strip() if value and value.strip() else None
