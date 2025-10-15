# backend/users/apps.py
"""
users アプリの設定ファイル

このファイルの役割:
- Django に「users というアプリがあるよ」と教える
- アプリの基本設定を行う
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """users アプリの設定クラス"""
    
    # データベースの主キー（ID）の型を設定
    default_auto_field = 'django.db.models.BigAutoField'
    
    # このアプリの名前（フォルダ名と一致させる）
    name = 'users'