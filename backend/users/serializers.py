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
    """
    ユーザー作成用シリアライザー（バリデーションのみ）
    
    注意: create() メソッドは定義しない
    実際の作成処理は UserService.create_user() で行う
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        max_length=128,
        error_messages={
            'min_length': 'パスワードは8文字以上で入力してください',
            'max_length': 'パスワードは128文字以内で入力してください',
            'required': 'パスワードは必須です',
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
    
    def validate_employee_id(self, value):
        """社員番号のバリデーション"""
        if not value or not value.strip():
            raise serializers.ValidationError('社員番号は必須です')
        
        value = value.strip()

        # 既存チェック（削除済みは除外）
        if User.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError(
                f'社員番号「{value}」は既に使用されています。別の社員番号を入力してください。'
            )
        
        return value
    
    def validate_username(self, value):
        """ユーザー名のバリデーション"""
        if not value or not value.strip():
            raise serializers.ValidationError('ユーザー名は必須です')
        
        return value.strip()
    
    def validate_email(self, value):
        """メールアドレスのバリデーション"""
        if value:
            value = value.strip().lower()
            
            # ⭐ メールアドレスをユニークにしたい場合
            # if User.objects.filter(email=value).exists():
            #     raise serializers.ValidationError(
            #         f'メールアドレス「{value}」は既に使用されています'
            #     )
            
            return value
        return None


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    ユーザー更新用シリアライザー（バリデーションのみ）
    
    注意: update() メソッドは定義しない
    実際の更新処理は UserService.update_user() で行う
    """
    
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={'input_type': 'password'},
        min_length=8,
        max_length=128,
        error_messages={
            'min_length': 'パスワードは8文字以上で入力してください',
            'max_length': 'パスワードは128文字以内で入力してください',
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
        """社員番号のバリデーション（更新時）"""
        if not value or not value.strip():
            raise serializers.ValidationError('社員番号は必須です')
        
        instance = self.instance
        value = value.strip()
        
        # ⭐ 自分以外で同じ社員番号が存在するかチェック
        if User.objects.filter(employee_id=value).exclude(id=instance.id).exists():
            raise serializers.ValidationError(
                f'社員番号「{value}」は既に使用されています。別の社員番号を入力してください。'
            )
        
        return value
    
    def validate_username(self, value):
        """ユーザー名のバリデーション"""
        if not value or not value.strip():
            raise serializers.ValidationError('ユーザー名は必須です')
        
        return value.strip()
    
    def validate_email(self, value):
        """メールアドレスのバリデーション"""
        if value:
            value = value.strip().lower()
            instance = self.instance
            
            # ⭐ 自分以外で同じメールアドレスがあるかチェック
            # if User.objects.filter(email=value).exclude(id=instance.id).exists():
            #     raise serializers.ValidationError(
            #         f'メールアドレス「{value}」は既に使用されています'
            #     )
            
            return value
        return None
    
    def validate_password(self, value):
        """パスワードのバリデーション"""
        if not value or not value.strip():
            return None
        return value