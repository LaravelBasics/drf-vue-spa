# C:\Users\pvufx\Desktop\template\backend\users\serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """ユーザーシリアライザー（一覧・詳細用）"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'employee_id', 'is_admin',
            'created_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """ユーザー作成用シリアライザー"""
    
    class Meta:
        model = User
        fields = ['username', 'employee_id', 'is_admin', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate_employee_id(self, value):
        """社員番号のバリデーション"""
        if len(str(value)) > 10:
            raise serializers.ValidationError(
                "社員番号は10桁以内で入力してください。"
            )
        return value
    
    def validate_username(self, value):
        """ユーザー名のバリデーション"""
        if len(value) > 20:
            raise serializers.ValidationError(
                "ユーザー名は20文字以内で入力してください。"
            )
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    """ユーザー更新用シリアライザー"""
    
    class Meta:
        model = User
        fields = ['username', 'employee_id', 'is_admin', 'is_active']
    
    def validate_employee_id(self, value):
        """社員番号のバリデーション"""
        if len(str(value)) > 10:
            raise serializers.ValidationError(
                "社員番号は10桁以内で入力してください。"
            )
        return value
    
    def validate_username(self, value):
        """ユーザー名のバリデーション"""
        if len(value) > 20:
            raise serializers.ValidationError(
                "ユーザー名は20文字以内で入力してください。"
            )
        return value