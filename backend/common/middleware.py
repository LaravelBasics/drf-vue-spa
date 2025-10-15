class LanguageMiddleware:
    """
    リクエストヘッダーから言語を設定するミドルウェア
    
    フロントエンドから Accept-Language ヘッダーを受け取って
    Django の言語設定を切り替える
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Accept-Language ヘッダーから言語を取得
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        
        if accept_language:
            # 'ja' または 'en' を抽出
            lang = accept_language.split(',')[0].split('-')[0].strip()
            
            if lang in ['ja', 'en']:
                from django.utils.translation import activate
                activate(lang)
        
        response = self.get_response(request)
        return response