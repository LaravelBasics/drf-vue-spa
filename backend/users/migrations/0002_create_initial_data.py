# users/migrations/0002_create_initial_data.py

from django.db import migrations
from django.utils import timezone
from django.contrib.auth.hashers import make_password


def create_initial_data(apps, schema_editor):
    """初期データ作成（デフォルトグループ + 管理者ユーザー）"""

    User = apps.get_model("users", "User")
    Group = apps.get_model("users", "Group")
    UserGroup = apps.get_model("users", "UserGroup")

    # --- 1. デフォルトグループの作成 ---
    DEFAULT_GROUP_ID = "A"
    DEFAULT_GROUP_NAME = "デフォルト管理者グループ"

    if not Group.objects.filter(group_id=DEFAULT_GROUP_ID).exists():
        admin_group = Group.objects.create(
            group_id=DEFAULT_GROUP_ID,
            group_name=DEFAULT_GROUP_NAME,
            is_active=True,
            created_at=timezone.now(),
        )
    else:
        admin_group = Group.objects.get(group_id=DEFAULT_GROUP_ID)

    # --- 2. 初期管理者ユーザーの作成 ---
    ADMIN_USER_ID = "9999"

    if not User.objects.filter(user_id=ADMIN_USER_ID).exists():
        # User.objects.create を使い、パスワードは手動でハッシュ化して渡す
        admin_user = User.objects.create(
            user_id=ADMIN_USER_ID,
            username="管理者",
            email="admin@example.com",
            password=make_password("test1234"),  # ハッシュ化
            is_admin=True,
            is_active=True,
            # Admin画面を使わない場合でも、モデル定義上必要なフラグ
            is_staff=True,
            is_superuser=True,
            created_at=timezone.now(),
        )
    else:
        admin_user = User.objects.get(user_id=ADMIN_USER_ID)

    # --- 3. グループ所属関係の作成 ---
    if not UserGroup.objects.filter(user=admin_user, group=admin_group).exists():
        UserGroup.objects.create(
            user=admin_user,
            group=admin_group,
            joined_at=timezone.now(),
        )


def reverse_func(apps, schema_editor):
    """ロールバック処理"""
    User = apps.get_model("users", "User")
    Group = apps.get_model("users", "Group")

    # 作成したデータを削除
    User.objects.filter(user_id="9999").delete()
    Group.objects.filter(group_id="A").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_initial_data, reverse_func),
    ]
