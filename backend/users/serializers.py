# backend/users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


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
        max_length=128
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
    
    def validate_employee_id(self, value):
        """社員番号のバリデーション"""
        if not value.strip():
            raise serializers.ValidationError('社員番号は必須です')
        
        # 既存チェック（論理削除済みも含む）
        if User.all_objects.filter(employee_id=value, deleted_at__isnull=True).exists():
            raise serializers.ValidationError('この社員番号は既に使用されています')
        
        return value.strip()
    
    def validate_email(self, value):
        """メールアドレスのバリデーション（必要に応じてユニークチェック）"""
        if value:
            # メールアドレスをユニークにしたい場合はコメント解除
            # if User.all_objects.filter(email=value, deleted_at__isnull=True).exists():
            #     raise serializers.ValidationError('このメールアドレスは既に使用されています')
            return value.strip().lower()
        return None
    
    def create(self, validated_data):
        """ユーザー作成"""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """ユーザー更新用シリアライザー"""
    
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={'input_type': 'password'},
        min_length=8,
        max_length=128
    )
    
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'is_admin',
            'is_active',
        ]
    
    def validate_email(self, value):
        """メールアドレスのバリデーション"""
        if value:
            instance = self.instance
            # 自分以外で同じメールアドレスがあるかチェック（必要に応じて）
            # if User.all_objects.filter(
            #     email=value,
            #     deleted_at__isnull=True
            # ).exclude(id=instance.id).exists():
            #     raise serializers.ValidationError('このメールアドレスは既に使用されています')
            return value.strip().lower()
        return None
    
    def update(self, instance, validated_data):
        """ユーザー更新"""
        password = validated_data.pop('password', None)
        
        # パスワード以外のフィールドを更新
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # パスワードが指定されている場合のみ更新
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


# ==================== 認証用シリアライザー ====================

class LoginSerializer(serializers.Serializer):
    """ログイン用シリアライザー"""
    
    # フィールド名は employee_id だが、フロントエンドとの互換性のため
    # 引数名は username のままにすることも可能
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