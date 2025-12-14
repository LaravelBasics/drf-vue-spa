# common/apps.py
"""
commonアプリ設定

inspectdbで取り込んだモデルを管理

★重要★
- ready() メソッドでシグナルをロード
- managed=False でもシグナルは正常動作
"""

from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "common"
    verbose_name = "共通モデル"

    def ready(self):
        """
        アプリケーション起動時にシグナルを読み込む

        ★Django公式推奨★
        - signals.py を import することで @receiver が実行される
        - 全モデル（managed=False含む）に自動接続される

        参考: https://docs.djangoproject.com/en/5.2/topics/signals/
        """
        # ★重要★ シグナルを確実にロードする
        # このインポートにより、@receiverデコレーターが実行され、
        # 全モデルにシグナルが接続されます
        import common.signals  # noqa: F401
