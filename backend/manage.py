#!/usr/bin/env python
"""
Django 管理コマンド実行ファイル

このファイルの役割:
- Django の管理コマンドを実行するためのエントリーポイント
- python manage.py [コマンド] で使用

よく使うコマンド:
- python manage.py runserver        # 開発サーバー起動
- python manage.py migrate          # マイグレーション実行
- python manage.py makemigrations   # マイグレーション作成
- python manage.py createsuperuser  # スーパーユーザー作成
- python manage.py shell            # Django シェル起動
- python manage.py test             # テスト実行
"""

import os
import sys


def main():
    """Django の管理タスクを実行"""
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django がインストールされていません。仮想環境を有効化してください。"
        ) from exc
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()


# ==================== よく使う管理コマンド ====================
"""
【開発中によく使うコマンド】

1. サーバー起動
python manage.py runserver
python manage.py runserver 8080  # ポート指定

2. マイグレーション
python manage.py makemigrations      # マイグレーション作成
python manage.py migrate             # データベースに適用
python manage.py showmigrations      # 適用状況確認

3. スーパーユーザー作成
python manage.py createsuperuser

4. Djangoシェル（対話モード）
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.all()

5. 静的ファイル収集（本番環境）
python manage.py collectstatic


【カスタム管理コマンド】

1. ダミーユーザー作成
python manage.py create_dummy_users --count=100 --password=test1234

2. 古いユーザー削除
python manage.py cleanup_deleted_users --days=90 --dry-run
"""