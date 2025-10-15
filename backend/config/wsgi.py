# backend/config/wsgi.py
"""
WSGI 設定（本番環境用）

このファイルの役割:
- 本番環境で Django アプリケーションを起動するための設定
- Apache, Nginx + Gunicorn などで使用

WSGI とは:
- Web Server Gateway Interface の略
- Python の Web アプリケーションと Web サーバーをつなぐ標準インターフェース

使い方（本番環境）:
gunicorn config.wsgi:application --bind 0.0.0.0:8000
"""

import os
from django.core.wsgi import get_wsgi_application

# 環境変数に Django 設定モジュールを指定
# DJANGO_SETTINGS_MODULE が設定されていない場合のデフォルト値
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# WSGI アプリケーションを取得
application = get_wsgi_application()