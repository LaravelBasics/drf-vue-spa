"""
ユーザー管理シリアライザー
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


USER_ID_UNIQUE_VALIDATOR = UniqueValidator(
    queryset=User.objects.all(), message=_("ユーザーIDは既に使用されています")
)


class UserSerializer(serializers.ModelSerializer):
    """ユーザー情報取得用"""

    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "email",
            "is_admin",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user_id", "created_at", "updated_at"]


class BaseUserSerializer(serializers.ModelSerializer):
    """共通バリデーション用ベースシリアライザー"""

    def validate_user_id(self, value):
        """ユーザーIDの正規化（空白削除）"""
        return value.strip() if value else value

    def validate_email(self, value):
        """メールアドレス正規化（小文字変換）"""
        return value.strip().lower() if value else None


class UserCreateSerializer(BaseUserSerializer):
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

    user_id = serializers.CharField(
        required=True,
        max_length=50,
        validators=[USER_ID_UNIQUE_VALIDATOR],
        error_messages={
            "required": _("ユーザーIDは必須です"),
            "blank": _("ユーザーIDは必須です"),
            "max_length": _("ユーザーIDは50文字以内で入力してください"),
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
            "user_id",
            "username",
            "email",
            "password",
            "is_admin",
        ]


class UserUpdateSerializer(BaseUserSerializer):
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

    user_id = serializers.CharField(
        max_length=50,
        error_messages={
            "required": _("ユーザーIDは必須です"),
            "blank": _("ユーザーIDは必須です"),
            "max_length": _("ユーザーIDは50文字以内で入力してください"),
        },
        read_only=True,  # 更新時はuser_idを変更不可
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
            "user_id",
            "username",
            "email",
            "password",
            "is_admin",
            "is_active",
        ]

    def validate_password(self, value):
        """パスワード検証（空白のみは変更なし）"""
        return value.strip() if value and value.strip() else None
