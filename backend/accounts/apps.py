# backend/accounts/apps.py
"""
accounts アプリの設定ファイル

このファイルの役割:
- Django に「accounts というアプリがあるよ」と教える
- アプリの基本設定を行う
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    accounts アプリの設定クラス
    
    変更点:
    - クラス名を ApiConfig → AccountsConfig に修正
      （accounts アプリなのに ApiConfig だと混乱するため）
    """
    
    # データベースの主キー（ID）の型を設定
    # BigAutoField = 大きな数字まで扱える自動採番ID
    default_auto_field = 'django.db.models.BigAutoField'
    
    # このアプリの名前（フォルダ名と一致させる）
    name = 'accounts'