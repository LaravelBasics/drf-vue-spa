# common/apps.py
"""
commonアプリ設定

inspectdbで取り込んだモデルを管理
"""

from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "common"
    verbose_name = "モデル"
