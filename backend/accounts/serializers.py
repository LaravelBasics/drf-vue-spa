# backend/accounts/serializers.py
"""
ログイン用のデータ検証（翻訳対応版）

改善ポイント:
1. エラーメッセージを gettext_lazy で翻訳対応
2. error_messages を明示的に定義
3. 社員番号の桁数を50に拡張（論理削除対応）⭐
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class LoginSerializer(serializers.Serializer):
    """ログイン画面で入力されるデータのチェック"""

    employee_id = serializers.CharField(
        max_length=50,  # ⭐ 20→50に拡張（models.py と合わせる）
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
        """
        全体のバリデーション

        空白だけの入力を防ぐ
        """
        employee_id = attrs.get("employee_id")
        password = attrs.get("password")

        # 空文字列チェック
        if not employee_id or not password:
            raise serializers.ValidationError(_("社員番号とパスワードは必須です"))

        return attrs


# ==================== 変更点のまとめ ====================
"""
✅ 改善ポイント:

1. gettext_lazy のインポート
   from django.utils.translation import gettext_lazy as _

2. error_messages を明示的に定義
   - 'required': _('社員番号は必須です')
   - 'blank': _('社員番号は必須です')

3. validate メソッドのエラーメッセージも翻訳対応
   raise serializers.ValidationError(_('社員番号とパスワードは必須です'))

4. ⭐ 社員番号の桁数を拡張
   max_length=20 → max_length=50
   - models.py の変更に合わせる
   - 論理削除時に社員番号をそのまま保持するため
   - 将来の拡張にも対応

これにより、ログイン画面のすべてのエラーメッセージが多言語対応され、
論理削除にも対応します。
"""
