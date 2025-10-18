class LanguageMiddleware:
    """
    リクエストヘッダーから言語を設定するミドルウェア
    
    フロントエンドから Accept-Language ヘッダーを受け取り
    Django の言語設定を切り替える
    
    例: Accept-Language: ja,en-US;q=0.9 → 'ja' を設定
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Accept-Language ヘッダーから言語を取得
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        
        if accept_language:
            try:
                # 'ja,en-US;q=0.9' → 'ja' を抽出
                lang = accept_language.split(',')[0].split('-')[0].strip()
                
                # 対応言語のみ設定（ja, en）
                if lang in ['ja', 'en']:
                    from django.utils.translation import activate
                    activate(lang)
            except (IndexError, AttributeError):
                # ヘッダーの形式が不正な場合は無視
                pass
        
        response = self.get_response(request)
        return response