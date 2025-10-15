# backend/users/services/__init__.py
"""
services パッケージの初期化

このファイルの役割:
- services フォルダを Python パッケージとして認識させる
- UserService を外部から簡単にインポートできるようにする

使い方:
from users.services import UserService  # ← これが可能になる

# __init__.py がないと以下のように書く必要がある:
# from users.services.user_service import UserService
"""

from .user_service import UserService

# __all__ = このパッケージから公開するクラス・関数のリスト
__all__ = ['UserService']
