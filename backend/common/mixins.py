# backend/common/mixins.py

from rest_framework import status
from rest_framework.response import Response


class ErrorResponseMixin:
    """エラーレスポンスの統一フォーマット"""
    
    def error_response(self, error_code, detail, status_code=status.HTTP_400_BAD_REQUEST):
        """
        統一されたエラーレスポンスを返す
        
        Args:
            error_code (str): エラーコード（i18n で翻訳される）
            detail (str): 詳細メッセージ（フォールバック＆ログ用）
            status_code (int): HTTPステータスコード
        
        Returns:
            Response: エラーレスポンス
        """
        return Response(
            {'error_code': error_code, 'detail': detail},
            status=status_code
        )
    
    @staticmethod
    def extract_error_message(error_detail):
        """
        DRF ValidationError の detail から メッセージを抽出
        
        ValidationError の detail は複数の形式を持つため、
        統一してメッセージ文字列に変換する
        
        Args:
            error_detail: ValidationError.detail
        
        Returns:
            str: エラーメッセージ
        
        Example:
            # dict の場合（フィールド別エラー）
            extract_error_message({'username': ['必須です']})
            → '必須です'
            
            # list の場合（複数エラー）
            extract_error_message(['エラー1', 'エラー2'])
            → 'エラー1'
            
            # str の場合
            extract_error_message('エラーメッセージ')
            → 'エラーメッセージ'
        """
        # フィールド別エラーの場合（dict）
        if isinstance(error_detail, dict):
            first_error = next(iter(error_detail.values()))
            if isinstance(first_error, list):
                return str(first_error[0])
            return str(first_error)
        
        # 複数エラーの場合（list）
        if isinstance(error_detail, list):
            return str(error_detail[0])
        
        # 単一エラーの場合（str）
        return str(error_detail)