# backend/users/serializers.py
"""
ユーザー管理のシリアライザー（改善版）

改善ポイント:
1. UniqueValidator で一元管理
2. 二重チェックを削除
3. UserCreateSerializer と UserUpdateSerializer でパターンを統一
4. 翻訳が確実に動作
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


# ==================== 共通のバリデーター ====================

EMPLOYEE_ID_UNIQUE_VALIDATOR = UniqueValidator(
    queryset=User.objects.all(),
    message=_('社員番号は既に使用されています')
)


# ==================== シリアライザー ====================

class UserSerializer(serializers.ModelSerializer):
    """ユーザー情報取得用シリアライザー"""
    
    display_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'employee_id',
            'username',
            'email',
            'display_name',
            'is_admin',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """ユーザー作成用シリアライザー"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        max_length=128,
        error_messages={
            'min_length': _('パスワードは8文字以上で入力してください'),
            'max_length': _('パスワードは128文字以内で入力してください'),
            'required': _('パスワードは必須です'),
        }
    )
    
    employee_id = serializers.CharField(
        required=True,
        validators=[EMPLOYEE_ID_UNIQUE_VALIDATOR],
        error_messages={
            'required': _('社員番号は必須です'),
            'blank': _('社員番号は必須です'),
        }
    )
    
    username = serializers.CharField(
        required=True,
        error_messages={
            'required': _('ユーザー名は必須です'),
            'blank': _('ユーザー名は必須です'),
        }
    )
    
    class Meta:
        model = User
        fields = [
            'employee_id',
            'username',
            'email',
            'password',
            'is_admin',
        ]
    
    def validate_email(self, value):
        """メールアドレスの正規化"""
        if value:
            return value.strip().lower()
        return None


class UserUpdateSerializer(serializers.ModelSerializer):
    """ユーザー更新用シリアライザー"""
    
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={'input_type': 'password'},
        min_length=8,
        max_length=128,
        error_messages={
            'min_length': _('パスワードは8文字以上で入力してください'),
            'max_length': _('パスワードは128文字以内で入力してください'),
        }
    )
    
    employee_id = serializers.CharField(
        required=True,
        error_messages={
            'required': _('社員番号は必須です'),
            'blank': _('社員番号は必須です'),
        }
    )
    
    username = serializers.CharField(
        required=True,
        error_messages={
            'required': _('ユーザー名は必須です'),
            'blank': _('ユーザー名は必須です'),
        }
    )
    
    class Meta:
        model = User
        fields = [
            'employee_id',
            'username',
            'email',
            'password',
            'is_admin',
            'is_active',
        ]
    
    def validate_employee_id(self, value):
        """
        社員番号の重複チェック（更新時）
        
        更新時は自分以外の重複をチェック
        """
        value = value.strip()
        instance = self.instance
        
        # 自分以外で同じ employee_id が存在するかチェック
        if User.objects.filter(employee_id=value).exclude(id=instance.id).exists():
            raise serializers.ValidationError(_('社員番号は既に使用されています'))
        
        return value
    
    def validate_email(self, value):
        """メールアドレスの正規化"""
        if value:
            return value.strip().lower()
        return None
    
    def validate_password(self, value):
        """パスワードの検証"""
        if not value or not value.strip():
            return None  # パスワード変更しない
        return value


# ==================== 変更点のまとめ ====================
"""
✅ 改善ポイント:

1. UserCreateSerializer
   - ❌ 削除: validate_employee_id での重複チェック（二重チェック）
   - ✅ 追加: employee_id フィールドに error_messages
   - ✅ 追加: username フィールドに error_messages
   - ✅ 保持: UniqueValidator による重複チェック

2. UserUpdateSerializer
   - ❌ 削除: 古い % フォーマットのメッセージ
   - ✅ 変更: シンプルなメッセージに統一
   - ✅ 追加: employee_id, username フィールドの明示的定義

3. 共通
   - ✅ email の正規化のみ validate メソッドで実施
   - ✅ その他は error_messages で対応
   - ✅ 翻訳メッセージの一貫性

バリデーションの役割分担:
- UniqueValidator: 重複チェック（作成時）
- validate_employee_id: 重複チェック（更新時、自分以外）
- error_messages: 必須チェック、文字数制限
- validate_email: 値の正規化（小文字変換）
"""