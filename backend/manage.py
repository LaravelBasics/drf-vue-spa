




# ==================== 1. manage.py ====================
# backend/manage.py
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

#!/usr/bin/env python
import os
import sys


def main():
    """
    Django の管理タスクを実行
    
    処理の流れ:
    1. DJANGO_SETTINGS_MODULE 環境変数を設定
    2. Django の管理コマンドをインポート
    3. コマンドを実行
    """
    
    # Django 設定モジュールを指定
    # 環境変数がない場合は 'config.settings' をデフォルトに設定
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        # Django の管理コマンドをインポート
        from django.core.management import execute_from_command_line
    
    except ImportError as exc:
        # Django がインストールされていない場合のエラーメッセージ
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # コマンドライン引数を渡して実行
    # sys.argv = ['manage.py', 'runserver', '8000']
    execute_from_command_line(sys.argv)


# このファイルが直接実行された場合のみ main() を実行
# import された場合は実行しない
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

5. データベースクリア
python manage.py flush

6. 静的ファイル収集（本番環境）
python manage.py collectstatic


【カスタム管理コマンド】

1. ダミーユーザー作成
python manage.py create_dummy_users --count=100 --password=test1234

2. 古いユーザー削除
python manage.py cleanup_deleted_users --days=90 --dry-run
"""