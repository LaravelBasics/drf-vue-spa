"""
共通エラーレスポンスミックスイン
"""

from rest_framework import status
from rest_framework.response import Response


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
        """
        # 文字列の場合
        if isinstance(error_detail, str):
            return str(error_detail)

        # リストの場合
        if isinstance(error_detail, list):
            return str(error_detail[0]) if error_detail else ""

        # 辞書の場合（フィールドエラー）
        if isinstance(error_detail, dict):
            first_value = next(iter(error_detail.values()), None)
            if isinstance(first_value, list) and first_value:
                return str(first_value[0])
            return str(first_value) if first_value else ""

        return str(error_detail)
