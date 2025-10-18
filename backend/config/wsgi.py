"""
WSGI 設定（本番環境用）

用途:
- Apache, Nginx + Gunicorn などで Django を起動

本番環境での起動例:
    gunicorn config.wsgi:application --bind 0.0.0.0:8000
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()