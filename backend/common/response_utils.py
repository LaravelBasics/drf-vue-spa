"""
レスポンス関連のユーティリティ関数
"""


def extract_validation_error(validation_error):
    """
    ValidationErrorから最初のエラーメッセージを抽出

    Args:
        validation_error: rest_framework.exceptions.ValidationError

    Returns:
        str: 最初のエラーメッセージ

    Examples:
        >>> from rest_framework.exceptions import ValidationError
        >>> from rest_framework.response import Response
        >>>
        >>> # 使い方
        >>> try:
        ...     serializer.is_valid(raise_exception=True)
        ... except ValidationError as e:
        ...     error_msg = extract_validation_error(e)
        ...     return Response({"detail": error_msg}, status=400)
    """
    # error_detailを取得
    error_detail = getattr(validation_error, "detail", str(validation_error))

    # 文字列の場合
    if isinstance(error_detail, str):
        return error_detail

    # リストの場合
    if isinstance(error_detail, list) and error_detail:
        return str(error_detail[0])

    # 辞書の場合(フィールドエラー)
    if isinstance(error_detail, dict):
        first_value = next(iter(error_detail.values()), None)
        if isinstance(first_value, list) and first_value:
            return str(first_value[0])
        if first_value:
            return str(first_value)

    # フォールバック
    return str(error_detail)
