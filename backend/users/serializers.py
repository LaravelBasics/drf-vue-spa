from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction

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
        fields = [
            'username', 'employee_id', 'is_admin', 'password'
        ]
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
    
    @transaction.atomic
    def create(self, validated_data):
        """ユーザー作成"""
        password = validated_data.pop('password', None)
        user = User.objects.create_user(
            password=password or 'defaultpassword123',
            **validated_data
        )
        return user

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
    
    def validate(self, attrs):
        """管理者の最低1人保証バリデーション"""
        instance = self.instance
        is_admin = attrs.get('is_admin', instance.is_admin)
        is_active = attrs.get('is_active', instance.is_active)
        
        # 現在のユーザーが管理者で、管理者権限を削除または非活性化する場合
        if instance.is_admin and (not is_admin or not is_active):
            # 他のアクティブな管理者の数をチェック
            active_admin_count = User.objects.filter(
                is_admin=True, 
                is_active=True
            ).exclude(id=instance.id).count()
            
            if active_admin_count == 0:
                raise serializers.ValidationError(
                    "管理者は最低1人必要です。最後の管理者の権限を削除することはできません。"
                )
        
        return attrs
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """ユーザー更新"""
        return super().update(instance, validated_data)