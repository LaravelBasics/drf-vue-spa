# backend/users/serializers.py
"""
ユーザー管理のシリアライザー（完全版）

改善ポイント:
1. UniqueValidator で作成・更新を一元管理
2. 不要な validate_employee_id メソッドを削除
3. DRFの標準機能のみで実装
4. シンプルで保守しやすいコード
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


# ==================== 共通のバリデーター ====================

EMPLOYEE_ID_UNIQUE_VALIDATOR = UniqueValidator(
    queryset=User.objects.all(), message=_("社員番号は既に使用されています")
)


# ==================== シリアライザー ====================


class UserSerializer(serializers.ModelSerializer):
    """ユーザー情報取得用シリアライザー"""

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
    """ユーザー作成用シリアライザー"""

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
        validators=[EMPLOYEE_ID_UNIQUE_VALIDATOR],
        error_messages={
            "required": _("社員番号は必須です"),
            "blank": _("社員番号は必須です"),
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
        """値の正規化のみ（空白削除）"""
        return value.strip() if value else value

    def validate_email(self, value):
        """メールアドレスの正規化（小文字変換）"""
        return value.strip().lower() if value else None


class UserUpdateSerializer(serializers.ModelSerializer):
    """ユーザー更新用シリアライザー"""

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
        validators=[EMPLOYEE_ID_UNIQUE_VALIDATOR],  # ⭐ 作成時と同じ！
        error_messages={
            "required": _("社員番号は必須です"),
            "blank": _("社員番号は必須です"),
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
        """値の正規化のみ（空白削除）"""
        return value.strip() if value else value

    def validate_email(self, value):
        """メールアドレスの正規化（小文字変換）"""
        return value.strip().lower() if value else None

    def validate_password(self, value):
        """
        パスワードの検証

        空白のみの場合は None を返す（パスワード変更なし）
        """
        return value.strip() if value and value.strip() else None


# ==================== 変更点のまとめ ====================
"""
✅ 最終改善ポイント:

1. 重複チェックの統一
   ❌ 削除: validate_employee_id での重複チェック（二重チェック）
   ✅ 統一: UniqueValidator のみで作成・更新両方対応
   
2. メソッドの役割を明確化
   ✅ validate_employee_id: 値の正規化のみ（strip）
   ✅ validate_email: 値の正規化のみ（小文字変換）
   ✅ validate_password: 空白チェックのみ
   
3. パフォーマンス改善
   ✅ データベースクエリが1回だけ（UniqueValidator）
   ❌ 以前: 2回（UniqueValidator + validate_employee_id）

4. コードの簡潔性
   ✅ 作成と更新でほぼ同じコード
   ✅ DRFの標準機能のみ使用
   ✅ カスタムバリデーター不要

バリデーションの流れ:
1. employee_id フィールドの検証
   - required チェック（error_messages）
   - UniqueValidator で重複チェック（自動で作成/更新を判定）
   - validate_employee_id で空白削除

2. 更新時の動作
   - serializer.instance が存在
   - UniqueValidator が自動で exclude(pk=instance.pk)
   - 自分以外の重複のみチェック

3. 作成時の動作
   - serializer.instance が None
   - UniqueValidator が全体をチェック
"""
