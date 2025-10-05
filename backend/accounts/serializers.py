# backend/accounts/serializers.py
from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    """
    ログインシリアライザー
    
    employee_id で認証を行うが、フロントエンドとの互換性のため
    フィールド名は柔軟に対応可能
    """
    employee_id = serializers.CharField(
        max_length=20,
        required=True,
        help_text='ログインに使用する社員番号'
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """認証バリデーション"""
        employee_id = attrs.get('employee_id')
        password = attrs.get('password')
        
        if not employee_id or not password:
            raise serializers.ValidationError('社員番号とパスワードは必須です')
        
        return attrs