"""
共通エラーレスポンスミックスイン

統一されたエラーレスポンス形式を提供。
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


class ErrorResponseMixin:
    """
    エラーレスポンスを統一するミックスイン

    Usage:
        class MyView(ErrorResponseMixin, APIView):
            def get(self, request):
                return self.error_response(
                    error_code='NOT_FOUND',
                    detail='ユーザーが見つかりません',
                    status_code=404
                )
    """

    def error_response(
        self, error_code=None, detail=None, status_code=status.HTTP_400_BAD_REQUEST
    ):
        """
        統一エラーレスポンス

        Args:
            error_code: エラーコード（例: 'NOT_FOUND'）
            detail: エラーメッセージ
            status_code: HTTPステータスコード

        Returns:
            Response: {'error_code': '...', 'detail': '...'}
        """
        response_data = {}

        if error_code:
            response_data["error_code"] = error_code

        if detail:
            response_data["detail"] = detail

        return Response(response_data, status=status_code)

    def validation_error_response(self, validation_error):
        """
        ValidationError を統一形式で返す

        Args:
            validation_error: rest_framework.exceptions.ValidationError

        Returns:
            Response: 400 Bad Request
        """
        if hasattr(validation_error, "detail"):
            error_msg = self.extract_error_message(validation_error.detail)
        else:
            error_msg = str(validation_error)

        return Response({"detail": error_msg}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def extract_error_message(error_detail):
        """
        DRF ValidationError から最初のエラーメッセージを抽出

        Args:
            error_detail: ValidationError.detail

        Returns:
            str: 最初のエラーメッセージ

        対応パターン:
            dict: {'employee_id': ['既に使用されています']}
            list: ['エラー1', 'エラー2']
            str:  'エラーメッセージ'
        """
        if isinstance(error_detail, dict):
            first_field_error = next(iter(error_detail.values()))

            if isinstance(first_field_error, list) and first_field_error:
                return str(first_field_error[0])

            return str(first_field_error)

        if isinstance(error_detail, list) and error_detail:
            return str(error_detail[0])

        return str(error_detail)
