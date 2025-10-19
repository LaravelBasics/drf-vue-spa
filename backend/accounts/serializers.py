"""
ログイン用シリアライザー
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class LoginSerializer(serializers.Serializer):
    """
    ログイン入力データのバリデーション

    Fields:
        employee_id: 社員番号（最大50文字）
        password: パスワード
    """

    employee_id = serializers.CharField(
        max_length=50,
        required=True,
        error_messages={
            "required": _("社員番号は必須です"),
            "blank": _("社員番号は必須です"),
        },
        help_text="社員番号を入力してください（例: EMP001）",
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
