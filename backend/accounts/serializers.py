# backend/accounts/serializers.py
"""
ログイン用のデータ検証（シリアライザー）

このファイルの役割:
- フロントエンドから送られてきたデータが正しいかチェックする
- 「社員番号」と「パスワード」が両方入力されているか確認
"""

from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """
    ログイン画面で入力されるデータのチェック
    
    フロントエンドから送られてくるデータ:
    {
        "employee_id": "EMP001",
        "password": "password123"
    }
    
    このクラスがやること:
    1. 社員番号が入力されているか？
    2. パスワードが入力されているか？
    3. どちらかが空ならエラーメッセージを返す
    """
    
    # 社員番号のフィールド定義
    employee_id = serializers.CharField(
        max_length=20,              # 最大20文字
        required=True,              # 必須項目
        help_text='社員番号を入力してください（例: EMP001）'
    )
    
    # パスワードのフィールド定義
    password = serializers.CharField(
        write_only=True,            # レスポンスに含めない（セキュリティ対策）
        required=True,              # 必須項目
        style={'input_type': 'password'}  # パスワード入力欄として表示
    )
    
    def validate(self, attrs):
        """
        全体のバリデーション（追加チェック）
        
        引数:
            attrs: 入力されたデータ
                  例: {'employee_id': 'EMP001', 'password': 'password123'}
        
        戻り値:
            チェックOKなら入力データをそのまま返す
            NGならエラーを発生させる
        """
        employee_id = attrs.get('employee_id')
        password = attrs.get('password')
        
        # 社員番号またはパスワードが空文字列の場合エラー
        # （空白だけの入力を防ぐ）
        if not employee_id or not password:
            raise serializers.ValidationError('社員番号とパスワードは必須です')
        
        # チェックOK
        return attrs