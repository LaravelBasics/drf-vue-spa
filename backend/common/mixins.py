# backend/common/mixins.py
"""
共通で使えるエラーレスポンス機能（確認版）

変更点:
- extract_error_message の処理を改善
- より多くのパターンに対応
"""

from rest_framework import status
from rest_framework.response import Response


class ErrorResponseMixin:
    """
    エラーレスポンスを統一するミックスイン
    
    使い方:
        class MyView(ErrorResponseMixin, APIView):
            def get(self, request):
                return self.error_response(
                    error_code='NOT_FOUND',
                    detail='ユーザーが見つかりません',
                    status_code=404
                )
    """
    
    def error_response(self, error_code=None, detail=None, status_code=status.HTTP_400_BAD_REQUEST):
        """
        統一されたエラーレスポンスを返す
        
        Args:
            error_code: エラーコード（Optional、ビジネスロジックエラー用）
            detail: 詳細メッセージ（Optional、Django が翻訳済み）
            status_code: HTTPステータスコード
        
        Returns:
            Response: エラーレスポンス
        
        使用例:
            # ビジネスロジックエラー（error_code + detail）
            return self.error_response(
                error_code='LAST_ADMIN',
                detail='最後の管理者は削除できません',
                status_code=400
            )
            
            # バリデーションエラー（detail のみ）
            return Response({'detail': 'エラーメッセージ'}, status=400)
        """
        response_data = {}
        
        if error_code:
            response_data['error_code'] = error_code
        
        if detail:
            response_data['detail'] = detail
        
        return Response(response_data, status=status_code)
    
    @staticmethod
    def extract_error_message(error_detail):
        """
        DRF の ValidationError から最初のエラーメッセージを取り出す
        
        Args:
            error_detail: ValidationError.detail
        
        Returns:
            str: 最初のエラーメッセージ
        
        対応パターン:
            1. dict: {'employee_id': ['既に使用されています']}
            2. list: ['エラー1', 'エラー2']
            3. str: 'エラーメッセージ'
            4. ErrorDetail: DRF の ErrorDetail オブジェクト
        
        例:
            {'username': ['必須です']} → '必須です'
            ['エラー1', 'エラー2'] → 'エラー1'
            'エラーメッセージ' → 'エラーメッセージ'
        """
        
        # パターン1: フィールド別エラー（dict）
        if isinstance(error_detail, dict):
            # 最初のフィールドのエラーを取得
            first_field_error = next(iter(error_detail.values()))
            
            # そのフィールドのエラーが list の場合
            if isinstance(first_field_error, list) and len(first_field_error) > 0:
                return str(first_field_error[0])
            
            # そのフィールドのエラーが文字列の場合
            return str(first_field_error)
        
        # パターン2: 複数エラー（list）
        if isinstance(error_detail, list) and len(error_detail) > 0:
            return str(error_detail[0])
        
        # パターン3: 単一エラー（str または ErrorDetail）
        return str(error_detail)


# ==================== テストケース ====================
"""
extract_error_message のテスト:

1. dict (フィールド別エラー)
   入力: {'employee_id': ['既に使用されています']}
   出力: '既に使用されています'

2. dict (複数フィールド)
   入力: {'employee_id': ['エラー1'], 'username': ['エラー2']}
   出力: 'エラー1' (最初のフィールド)

3. list
   入力: ['エラー1', 'エラー2']
   出力: 'エラー1'

4. str
   入力: 'エラーメッセージ'
   出力: 'エラーメッセージ'

5. ErrorDetail (DRF)
   入力: ErrorDetail('必須です', code='required')
   出力: '必須です'
"""