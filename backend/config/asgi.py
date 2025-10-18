"""
ASGI 設定（非同期処理用）

用途:
- WebSocket, Server-Sent Events などの非同期通信
- HTTP/2 対応

本番環境での起動:
    daphne config.asgi:application

注意:
- 通常の REST API のみなら WSGI で十分
- WebSocket を使う場合のみ ASGI が必要
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()