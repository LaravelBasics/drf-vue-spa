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
    """初期管理者ユーザーを作成"""
    User = apps.get_model('users', 'User')
    
    # 既に管理者が存在する場合はスキップ
    if User.objects.filter(employee_id='9999').exists():
        return
    
    from django.contrib.auth.hashers import make_password
    
    User.objects.create(
        employee_id='9999',
        username='管理者',
        email='admin@example.com',
        password=make_password('test1234'),
        is_admin=True,
        is_staff=True,
        is_superuser=True,
        is_active=True,
    )


def reverse_func(apps, schema_editor):
    """ロールバック処理（マイグレーションを戻す時）"""
    User = apps.get_model('users', 'User')
    User.objects.filter(employee_id='9999').delete()


class Migration(migrations.Migration):
    """マイグレーションクラス"""
    
    dependencies = [
        ('users', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(create_initial_superuser, reverse_func),
    ]


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