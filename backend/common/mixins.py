"""
共通エラーレスポンス機能

使い方:
    class MyView(ErrorResponseMixin, APIView):
        def get(self, request):
            return self.error_response(
                error_code='NOT_FOUND',
                detail='ユーザーが見つかりません',
                status_code=404
            )
"""

from rest_framework import status
from rest_framework.response import Response


class ErrorResponseMixin:
    """エラーレスポンスを統一するミックスイン"""
    
    def error_response(self, error_code=None, detail=None, status_code=status.HTTP_400_BAD_REQUEST):
        """
        統一されたエラーレスポンスを返す
        
        Args:
            error_code: エラーコード（例: 'NOT_FOUND'）
            detail: エラーメッセージ
            status_code: HTTPステータスコード
        
        Returns:
            Response: {'error_code': '...', 'detail': '...'}
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
        DRF の ValidationError から最初のエラーメッセージを抽出
        
        Args:
            error_detail: ValidationError.detail
        
        Returns:
            str: 最初のエラーメッセージ
        
        対応パターン:
            dict: {'employee_id': ['既に使用されています']}
            list: ['エラー1', 'エラー2']
            str:  'エラーメッセージ'
        """
        
        # dict: フィールド別エラー
        if isinstance(error_detail, dict):
            first_field_error = next(iter(error_detail.values()))
            
            if isinstance(first_field_error, list) and first_field_error:
                return str(first_field_error[0])
            
            return str(first_field_error)
        
        # list: 複数エラー
        if isinstance(error_detail, list) and error_detail:
            return str(error_detail[0])
        
        # str: 単一エラー
        return str(error_detail)