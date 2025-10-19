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
        Accept-Language: fr → デフォルト言語にフォールバック
    """

    # 対応言語
    SUPPORTED_LANGS = {"ja", "en"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")

        if accept_language:
            lang = self._parse_language(accept_language)
            if lang:
                activate(lang)

        return self.get_response(request)

    def _parse_language(self, accept_language):
        """
        Accept-Language ヘッダーをパースして対応言語コードを返す

        Args:
            accept_language: Accept-Language ヘッダーの値

        Returns:
            str: 対応言語コード or None

        Examples:
            'ja,en-US;q=0.9' → 'ja'
            'en-GB,en' → 'en'
            'fr,de' → None（未対応）
            'invalid;;data' → None
        """
        try:
            # 最初の言語を抽出: 'ja,en-US;q=0.9' → 'ja'
            lang = accept_language.split(",")[0].split("-")[0].strip().lower()

            # 対応言語のみ返す
            if lang in self.SUPPORTED_LANGS:
                return lang

        except (IndexError, AttributeError, ValueError):
            # 不正なヘッダーは無視
            pass

        return None
