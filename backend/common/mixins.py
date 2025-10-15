# backend/common/mixins.py
"""
共通で使えるエラーレスポンス機能

このファイルの役割:
- エラーレスポンスの形式を統一する
- バリデーションエラーのメッセージを取り出す
"""

from rest_framework import status
from rest_framework.response import Response


class ErrorResponseMixin:
    """
    エラーレスポンスを統一するミックスイン
    
    ミックスインとは:
    - 他のクラスに「機能を追加する」ための部品
    - このクラスを継承すると error_response() メソッドが使えるようになる
    
    使い方:
    class MyView(ErrorResponseMixin, APIView):
        def get(self, request):
            return self.error_response('NOT_FOUND', 'ユーザーが見つかりません')
    """
    
    def error_response(self, error_code, detail, status_code=status.HTTP_400_BAD_REQUEST):
        """
        統一されたエラーレスポンスを返す
        
        引数:
            error_code: エラーの種類を表すコード（例: 'NOT_FOUND', 'VALIDATION_ERROR'）
                       フロントエンドがこのコードを見て翻訳メッセージを表示する
            detail: 詳しいエラーメッセージ（日本語でOK）
            status_code: HTTPステータスコード（デフォルト: 400）
        
        戻り値:
            Response: 以下の形式のJSONレスポンス
            {
                "error_code": "NOT_FOUND",
                "detail": "ユーザーが見つかりません"
            }
        
        使用例:
            # ユーザーが見つからない場合
            return self.error_response('NOT_FOUND', 'ユーザーが見つかりません', 404)
            
            # バリデーションエラーの場合
            return self.error_response('VALIDATION_ERROR', '社員番号は必須です')
        """
        return Response(
            {'error_code': error_code, 'detail': detail},
            status=status_code
        )
    
    @staticmethod
    def extract_error_message(error_detail):
        """
        DRF（Django REST Framework）のバリデーションエラーから
        メッセージを取り出す
        
        なぜ必要？:
        DRFのエラーは複雑な形式で返ってくるため、
        最初のエラーメッセージだけを取り出して表示する
        
        引数:
            error_detail: ValidationError.detail（複雑な形式）
        
        戻り値:
            str: 最初のエラーメッセージ
        
        例:
            # パターン1: フィールドごとのエラー（辞書型）
            {'username': ['必須です'], 'email': ['無効なメールアドレスです']}
            → '必須です' を返す
            
            # パターン2: 複数エラー（リスト型）
            ['エラー1', 'エラー2']
            → 'エラー1' を返す
            
            # パターン3: 単一エラー（文字列型）
            'エラーメッセージ'
            → 'エラーメッセージ' をそのまま返す
        """
        
        # パターン1: フィールド別エラーの場合（dict）
        # 例: {'username': ['必須です'], 'email': ['無効です']}
        if isinstance(error_detail, dict):
            # 最初のフィールドのエラーを取得
            first_error = next(iter(error_detail.values()))
            
            # エラーがリストの場合、最初のメッセージを取得
            if isinstance(first_error, list):
                return str(first_error[0])
            
            # エラーが文字列の場合、そのまま返す
            return str(first_error)
        
        # パターン2: 複数エラーの場合（list）
        # 例: ['エラー1', 'エラー2']
        if isinstance(error_detail, list):
            return str(error_detail[0])
        
        # パターン3: 単一エラーの場合（str）
        # 例: 'エラーメッセージ'
        return str(error_detail)