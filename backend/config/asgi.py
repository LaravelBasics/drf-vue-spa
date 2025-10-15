# backend/config/asgi.py
"""
ASGI 設定（非同期処理用）

このファイルの役割:
- 非同期処理が必要な場合に使用
- WebSocket, リアルタイム通信などで使用

ASGI とは:
- Asynchronous Server Gateway Interface の略
- WSGI の非同期版
- WebSocket, HTTP/2, Server-Sent Events などに対応

使い方（本番環境）:
daphne config.asgi:application

注意:
- 通常の REST API だけなら WSGI で十分
- WebSocket を使う場合のみ ASGI が必要
"""

import os
from django.core.asgi import get_asgi_application

# 環境変数に Django 設定モジュールを指定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# ASGI アプリケーションを取得
application = get_asgi_application()