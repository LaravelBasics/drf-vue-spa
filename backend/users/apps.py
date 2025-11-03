"""
users アプリの設定ファイル
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """users アプリの設定クラス"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        """
        アプリ起動時の初期化処理

        Note:
            監査ログのシグナルは@receiverデコレーターで自動登録されるため
            明示的な登録処理は不要
        """
        # シグナルをインポートして登録を有効化
        import common.signals  # noqa: F401
