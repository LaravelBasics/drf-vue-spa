"""
カスタムミドルウェア
"""

from django.utils.translation import activate


class LanguageMiddleware:
    """
    Accept-Language ヘッダーから言語を設定

    フロントエンドから送信されたヘッダーに基づいて
    Djangoの言語設定を動的に切り替える。

    Example:
        Accept-Language: ja,en-US;q=0.9 → 'ja' を設定
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")

        if accept_language:
            try:
                # 'ja,en-US;q=0.9' → 'ja' を抽出
                lang = accept_language.split(",")[0].split("-")[0].strip()

                # 対応言語のみ設定
                if lang in ["ja", "en"]:
                    activate(lang)
            except (IndexError, AttributeError):
                pass

        response = self.get_response(request)
        return response
