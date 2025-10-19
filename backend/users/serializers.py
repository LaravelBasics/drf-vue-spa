# backend/users/serializers.py
"""
ユーザー管理のシリアライザー（完全版）

改善ポイント:
1. UniqueValidator で作成・更新を一元管理
2. 不要な validate_employee_id メソッドを削除
3. DRFの標準機能のみで実装
4. シンプルで保守しやすいコード
5. 社員番号の桁数を50に拡張（論理削除対応）⭐
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
        max_length=50,  # ⭐ 20→50に拡張（models.py と合わせる）
        validators=[EMPLOYEE_ID_UNIQUE_VALIDATOR],
        error_messages={
            "required": _("社員番号は必須です"),
            "blank": _("社員番号は必須です"),
            "max_length": _("社員番号は50文字以内で入力してください"),  # ⭐ 追加
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
        """
        値の正規化のみ（空白削除）

        ⭐ 重複チェックは UniqueValidator が自動で行う
        - 作成時: 全体で重複チェック
        - 更新時: 自分以外で重複チェック（UniqueValidator が自動判定）
        """
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
        max_length=50,  # ⭐ 20→50に拡張（models.py と合わせる）
        validators=[EMPLOYEE_ID_UNIQUE_VALIDATOR],  # ⭐ 作成時と同じ！
        error_messages={
            "required": _("社員番号は必須です"),
            "blank": _("社員番号は必須です"),
            "max_length": _("社員番号は50文字以内で入力してください"),  # ⭐ 追加
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
        """
        値の正規化のみ（空白削除）

        ⭐ UniqueValidator が自動で以下を判定:
        - 作成時: queryset 全体で重複チェック
        - 更新時: 自分（instance）以外で重複チェック
        """
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

5. ⭐ 社員番号の桁数拡張
   ✅ max_length=20 → max_length=50
   ✅ models.py の変更に合わせる
   ✅ 論理削除で番号をそのまま保持するため
   ✅ 将来の拡張にも対応


バリデーションの流れ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. employee_id フィールドの検証
   ① max_length チェック（50文字以内）
   ② required チェック（error_messages）
   ③ UniqueValidator で重複チェック（自動で作成/更新を判定）
   ④ validate_employee_id で空白削除

2. 更新時の動作
   - serializer.instance が存在
   - UniqueValidator が自動で exclude(pk=instance.pk)
   - 自分以外の重複のみチェック

3. 作成時の動作
   - serializer.instance が None
   - UniqueValidator が全体をチェック


論理削除との連携:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 削除時
   - employee_id はそのまま保持
   - deleted_at に日時を設定
   - 条件付きユニーク制約から外れる

2. 再利用時
   - 同じ employee_id で新規作成可能
   - UniqueValidator は User.objects（削除済み除外）を検索
   - 削除済みは検索対象外なので重複エラーにならない

3. 履歴追跡
   - User.all_objects.filter(employee_id="1000")
   - 削除済みも含めて検索可能
   - 監査・履歴確認に使用


使用例:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 作成
serializer = UserCreateSerializer(data={
    'employee_id': '1000',  # 最大50文字
    'username': '山田太郎',
    'password': 'password123',
    'is_admin': False
})

# 更新
serializer = UserUpdateSerializer(user_instance, data={
    'employee_id': '1001',  # 最大50文字
    'username': '山田次郎',
}, partial=True)
"""
