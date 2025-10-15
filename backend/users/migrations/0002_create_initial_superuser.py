# backend/users/migrations/0002_create_initial_superuser.py
"""
初期管理者ユーザー作成マイグレーション

このファイルの役割:
- データベース作成時に自動的に管理者ユーザーを作成
- python manage.py migrate 実行時に自動実行

なぜ必要？:
- 管理画面にログインするために最低1人の管理者が必要
- 手動で createsuperuser を実行する手間を省く
"""

from django.db import migrations


def create_initial_superuser(apps, schema_editor):
    """
    初期管理者ユーザーを作成
    
    作成するユーザー:
    - 社員番号: 9999（認証ID）
    - ユーザー名: 管理者（表示名）
    - パスワード: test1234
    - 権限: 管理者・スタッフ・スーパーユーザー
    """
    User = apps.get_model('users', 'User')
    
    # 既に管理者が存在する場合はスキップ
    if User.objects.filter(is_admin=True).exists():
        return
    
    # employee_id で管理者が存在しないか確認
    if not User.objects.filter(employee_id='9999').exists():
        # ⚠️ マイグレーション内では create_superuser は使えない
        # 理由: マイグレーション実行時はモデルの最終状態が分からないため
        from django.contrib.auth.hashers import make_password
        
        User.objects.create(
            employee_id='9999',    # ← 認証ID（ユニーク）
            username='管理者',      # ← 表示名（重複OK）
            email='admin@example.com',
            password=make_password('test1234'),  # ← パスワードをハッシュ化
            is_admin=True,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )


def reverse_func(apps, schema_editor):
    """
    ロールバック処理（マイグレーションを戻す時）
    
    python manage.py migrate users 0001 を実行すると呼ばれる
    """
    User = apps.get_model('users', 'User')
    User.objects.filter(employee_id='9999').delete()


class Migration(migrations.Migration):
    """マイグレーションクラス"""
    
    # 前のマイグレーション（0001_initial）に依存
    dependencies = [
        ('users', '0001_initial'),
    ]
    
    # 実行する処理
    operations = [
        # Python 関数を実行（create_initial_superuser と reverse_func）
        migrations.RunPython(create_initial_superuser, reverse_func),
    ]


# ==================== WSGI vs ASGI ====================
"""
WSGI と ASGI の違い:

【WSGI（同期処理）】
- 用途: 通常の REST API
- 特徴: 1リクエストごとに処理
- サーバー: Gunicorn, uWSGI
- 使用例: GET /api/users/

【ASGI（非同期処理）】
- 用途: WebSocket, リアルタイム通信
- 特徴: 複数のリクエストを並行処理
- サーバー: Daphne, Uvicorn
- 使用例: WebSocket チャット, リアルタイム通知


このプロジェクトでは:
- REST API のみ → WSGI で十分
- WebSocket を追加する場合 → ASGI に変更


本番環境での起動例:

# WSGI（通常の REST API）
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4

# ASGI（WebSocket 対応）
daphne -b 0.0.0.0 -p 8000 config.asgi:application
"""


# ==================== マイグレーションの仕組み ====================
"""
マイグレーションとは:
- データベースのスキーマ（テーブル構造）の変更履歴
- モデルの変更を自動的にデータベースに反映

マイグレーションの流れ:

1. モデルを変更
   models.py を編集

2. マイグレーションファイル作成
   python manage.py makemigrations
   → users/migrations/0003_alter_user_email.py が作成される

3. データベースに反映
   python manage.py migrate
   → データベーステーブルが変更される


マイグレーションの種類:

- 0001_initial.py: 初期テーブル作成
- 0002_create_initial_superuser.py: データ追加
- 0003_alter_user_email.py: フィールド変更
- 0004_user_phone.py: フィールド追加


マイグレーションの確認:

# 適用済みマイグレーション確認
python manage.py showmigrations

# マイグレーションの SQL を確認
python manage.py sqlmigrate users 0002

# マイグレーションを戻す
python manage.py migrate users 0001
"""
