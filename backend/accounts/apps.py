"""
accounts アプリの設定ファイル

このファイルの役割:
- Django に accounts アプリを認識させる
- アプリの基本設定を行う
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """accounts アプリの設定クラス"""
    
    # データベースの主キー（ID）の型
    # BigAutoField = 大きな整数まで扱える自動採番ID
    default_auto_field = 'django.db.models.BigAutoField'
    
    # アプリ名（フォルダ名と一致させる）
    name = 'accounts'