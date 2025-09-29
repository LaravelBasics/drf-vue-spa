# users/migrations/0002_auto_20250929_2249.py (ファイル名は合わせること)

from django.db import migrations

def create_initial_superuser(apps, schema_editor):
    # 'users' アプリの 'CustomUser' モデルを取得
    CustomUser = apps.get_model('users', 'CustomUser')
    
    # ユーザーがまだ存在しない場合のみ作成
    if not CustomUser.objects.filter(username='admin').exists():
        CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            # ★ パスワードは後で変更してください
            password='testtastaoL1!', 
            # ★ 必須フィールドである employee_id にユニークな値を設定
            employee_id=9999
        )

class Migration(migrations.Migration):

    dependencies = [
        # 1つ前のマイグレーションファイルを指定 (通常は initial)
        ('users', '0001_initial'), 
    ]

    operations = [
        # データ投入関数を実行
        migrations.RunPython(create_initial_superuser, reverse_code=migrations.RunPython.noop),
    ]