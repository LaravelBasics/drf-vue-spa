# backend/users/serializers.py
"""
ユーザー管理のシリアライザー

このファイルの役割:
- フロントエンドから送られてきたデータを検証（バリデーション）
- データベースとJSON形式の相互変換
- エラーメッセージの管理

シリアライザーとは:
- データの「通訳」のような役割
- フロントエンド ⇔ Django ⇔ データベース の間でデータを変換
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


# ==================== 1. ユーザー情報取得用 ====================

class UserSerializer(serializers.ModelSerializer):
    """
    ユーザー情報を返す時に使うシリアライザー
    
    使われる場面:
    - GET /api/users/ (一覧)
    - GET /api/users/{id}/ (詳細)
    - ログイン後のユーザー情報
    
    返されるJSON例:
    {
        "id": 1,
        "employee_id": "EMP001",
        "username": "山田太郎",
        "email": "yamada@example.com",
        "display_name": "山田太郎",
        "is_admin": false,
        "is_active": true,
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z"
    }
    """
    
    # display_name は models.py の @property で定義
    # read_only=True で読み取り専用（送信はできない）
    display_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        
        # APIで返すフィールド
        fields = [
            'id',
            'employee_id',
            'username',
            'email',
            'display_name',  # カスタムフィールド
            'is_admin',
            'is_active',
            'created_at',
            'updated_at',
        ]
        
        # 読み取り専用（変更不可）フィールド
        read_only_fields = ['id', 'created_at', 'updated_at']


# ==================== 2. ユーザー作成用 ====================

class UserCreateSerializer(serializers.ModelSerializer):
    """
    ユーザー作成時に使うシリアライザー
    
    使われる場面:
    - POST /api/users/
    
    受け取るJSON例:
    {
        "employee_id": "EMP001",
        "username": "山田太郎",
        "email": "yamada@example.com",
        "password": "password123",
        "is_admin": false
    }
    
    注意:
    - create() メソッドは定義しない
    - 実際の作成処理は UserService.create_user() で行う
    - このクラスはバリデーション（検証）のみ担当
    """
    
    # パスワードフィールドの定義
    password = serializers.CharField(
        write_only=True,        # レスポンスに含めない（セキュリティ）
        required=True,          # 必須項目
        style={'input_type': 'password'},  # 入力欄をパスワード型に
        min_length=8,           # 最小8文字
        max_length=128,         # 最大128文字
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
    
    # ==================== バリデーション ====================
    
    def validate_employee_id(self, value):
        """
        社員番号の検証
        
        チェック内容:
        1. 空文字列でないか
        2. 既に使われていないか
        
        引数:
            value: 入力された社員番号
        
        戻り値:
            検証済みの社員番号
        
        エラー:
            ValidationError: 検証失敗時
        """
        # 空文字列・空白のみをチェック
        if not value or not value.strip():
            raise serializers.ValidationError('社員番号は必須です')
        
        # 前後の空白を削除
        value = value.strip()

        # 重複チェック（削除済みは除外）
        if User.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError(
                f'社員番号「{value}」は既に使用されています。別の社員番号を入力してください。'
            )
        
        return value
    
    def validate_username(self, value):
        """
        ユーザー名の検証
        
        チェック内容:
        - 空文字列でないか
        """
        if not value or not value.strip():
            raise serializers.ValidationError('ユーザー名は必須です')
        
        return value.strip()
    
    def validate_email(self, value):
        """
        メールアドレスの検証
        
        チェック内容:
        - 小文字に変換
        - （オプション）重複チェック
        """
        if value:
            value = value.strip().lower()
            
            # ⭐ メールアドレスをユニークにしたい場合はコメント解除
            # if User.objects.filter(email=value).exists():
            #     raise serializers.ValidationError(
            #         f'メールアドレス「{value}」は既に使用されています'
            #     )
            
            return value
        return None


# ==================== 3. ユーザー更新用 ====================

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    ユーザー更新時に使うシリアライザー
    
    使われる場面:
    - PUT /api/users/{id}/
    - PATCH /api/users/{id}/
    
    受け取るJSON例:
    {
        "employee_id": "EMP001",
        "username": "山田太郎",
        "email": "yamada@example.com",
        "password": "newpassword123",  // 任意
        "is_admin": false,
        "is_active": true
    }
    
    注意:
    - update() メソッドは定義しない
    - 実際の更新処理は UserService.update_user() で行う
    - このクラスはバリデーション（検証）のみ担当
    """
    
    # パスワードフィールドの定義
    password = serializers.CharField(
        write_only=True,
        required=False,         # 任意項目（更新時はパスワード変更しないこともある）
        allow_blank=True,       # 空文字列OK（変更しない場合）
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
    
    # ==================== バリデーション ====================
    
    def validate_employee_id(self, value):
        """
        社員番号の検証（更新時）
        
        チェック内容:
        1. 空文字列でないか
        2. 自分以外で同じ社員番号が使われていないか
        
        更新時の注意点:
        - 自分自身の社員番号はOK（変更していない場合）
        - 他のユーザーと重複したらNG
        """
        if not value or not value.strip():
            raise serializers.ValidationError('社員番号は必須です')
        
        # 更新対象のユーザー
        instance = self.instance
        value = value.strip()
        
        # 自分以外で同じ社員番号が存在するかチェック
        if User.objects.filter(employee_id=value).exclude(id=instance.id).exists():
            raise serializers.ValidationError(
                f'社員番号「{value}」は既に使用されています。別の社員番号を入力してください。'
            )
        
        return value
    
    def validate_username(self, value):
        """ユーザー名の検証"""
        if not value or not value.strip():
            raise serializers.ValidationError('ユーザー名は必須です')
        
        return value.strip()
    
    def validate_email(self, value):
        """メールアドレスの検証（更新時）"""
        if value:
            value = value.strip().lower()
            instance = self.instance
            
            # ⭐ メールアドレスをユニークにしたい場合はコメント解除
            # if User.objects.filter(email=value).exclude(id=instance.id).exists():
            #     raise serializers.ValidationError(
            #         f'メールアドレス「{value}」は既に使用されています'
            #     )
            
            return value
        return None
    
    def validate_password(self, value):
        """
        パスワードの検証
        
        更新時の特別処理:
        - 空文字列の場合は None を返す（パスワード変更しない）
        - 値がある場合のみ更新する
        """
        if not value or not value.strip():
            return None  # パスワード変更しない
        return value


# ==================== シリアライザーの使い分け ====================
"""
3つのシリアライザーの役割:

1. UserSerializer
   - 用途: ユーザー情報を返す（一覧・詳細）
   - 特徴: display_name など読み取り専用フィールドがある
   - 使用場面: GET リクエスト

2. UserCreateSerializer
   - 用途: ユーザー作成時のバリデーション
   - 特徴: password が必須、重複チェック
   - 使用場面: POST /api/users/

3. UserUpdateSerializer
   - 用途: ユーザー更新時のバリデーション
   - 特徴: password が任意、自分以外との重複チェック
   - 使用場面: PUT/PATCH /api/users/{id}/


views.py での使い方:

class UserViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
"""


# ==================== バリデーションの流れ ====================
"""
シリアライザーでのバリデーション順序:

1. フィールドレベルのバリデーション
   - validate_{field_name} メソッドが自動的に呼ばれる
   - 例: validate_employee_id(), validate_username()

2. オブジェクトレベルのバリデーション
   - validate() メソッドが呼ばれる（複数フィールドの相関チェック）

3. is_valid() の結果
   - 全て通過 → True, validated_data にクリーンなデータ
   - 失敗 → False, errors にエラーメッセージ


使用例:

serializer = UserCreateSerializer(data=request.data)
if serializer.is_valid():
    # バリデーション成功
    clean_data = serializer.validated_data
    user = UserService.create_user(clean_data)
else:
    # バリデーション失敗
    errors = serializer.errors
    # {'employee_id': ['社員番号は必須です']}
"""


# ==================== よくあるエラーパターン ====================
"""
エラーメッセージの形式:

1. フィールドごとのエラー（dict）
{
    "employee_id": ["社員番号「EMP001」は既に使用されています"],
    "password": ["パスワードは8文字以上で入力してください"]
}

2. 全体のエラー（list）
["社員番号とパスワードは必須です"]

3. 詳細エラー（dict + list）
{
    "employee_id": [
        ErrorDetail(string='必須です', code='required')
    ]
}


フロントエンドでの処理例:

if (error.response.data.employee_id) {
    // フィールド別エラー
    alert(error.response.data.employee_id[0])
} else if (error.response.data.detail) {
    // 全体エラー
    alert(error.response.data.detail)
}
"""