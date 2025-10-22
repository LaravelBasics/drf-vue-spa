"""
users アプリの設定ファイル
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """users アプリの設定クラス"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        """アプリ起動時にシグナルを登録"""
        from common.signals import register_audit_signals

        register_audit_signals()  # ⭐ 全モデルに適用
