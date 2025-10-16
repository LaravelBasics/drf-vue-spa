# backend/accounts/serializers.py
"""
ログイン用のデータ検証（翻訳対応版）

改善ポイント:
1. エラーメッセージを gettext_lazy で翻訳対応
2. error_messages を明示的に定義
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class LoginSerializer(serializers.Serializer):
    """ログイン画面で入力されるデータのチェック"""
    
    employee_id = serializers.CharField(
        max_length=20,
        required=True,
        error_messages={
            'required': _('社員番号は必須です'),
            'blank': _('社員番号は必須です'),
        },
        help_text='社員番号を入力してください（例: EMP001）'
    )
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            'required': _('パスワードは必須です'),
            'blank': _('パスワードは必須です'),
        },
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """
        全体のバリデーション
        
        空白だけの入力を防ぐ
        """
        employee_id = attrs.get('employee_id')
        password = attrs.get('password')
        
        # 空文字列チェック
        if not employee_id or not password:
            raise serializers.ValidationError(
                _('社員番号とパスワードは必須です')
            )
        
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

これにより、ログイン画面のすべてのエラーメッセージが多言語対応されます。
"""