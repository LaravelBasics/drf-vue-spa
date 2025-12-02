# users/migrations/0002_create_initial_superuser.py

from django.db import migrations
from django.utils import timezone


def create_initial_superuser(apps, schema_editor):
    """初期管理者ユーザーを作成し、デフォルトグループ('A')に所属させる"""

    # マイグレーション時の状態のモデルを取得
    User = apps.get_model("users", "User")
    Group = apps.get_model("users", "Group")
    UserGroup = apps.get_model("users", "UserGroup")

    # --- 1. デフォルトグループの作成 ('A') ---
    DEFAULT_GROUP_ID = "A"
    DEFAULT_GROUP_NAME = "デフォルト管理者グループ"

    # 既にグループが存在する場合はスキップ
    if not Group.objects.filter(group_id=DEFAULT_GROUP_ID).exists():
        Group.objects.create(
            group_id=DEFAULT_GROUP_ID,
            group_name=DEFAULT_GROUP_NAME,
            is_active=True,
            created_at=timezone.now(),
        )

    admin_group = Group.objects.get(group_id=DEFAULT_GROUP_ID)

    # --- 2. 初期管理者ユーザーの作成 ('9999') ---
    ADMIN_USER_ID = "9999"

    # 既に管理者が存在する場合は、グループ所属処理に進む
    if User.objects.filter(user_id=ADMIN_USER_ID).exists():
        admin_user = User.objects.get(user_id=ADMIN_USER_ID)
    else:
        from django.contrib.auth.hashers import make_password

        admin_user = User.objects.create(
            user_id=ADMIN_USER_ID,
            username="管理者",
            email="admin@example.com",
            password=make_password("test1234"),
            is_admin=True,
            is_staff=True,
            is_superuser=True,
            is_active=True,
            created_at=timezone.now(),
        )

    # --- 3. 管理者ユーザーをグループに所属させる ---
    # UserGroup中間テーブルを使って所属関係を作成
    if not UserGroup.objects.filter(user=admin_user, group=admin_group).exists():
        UserGroup.objects.create(
            user=admin_user,
            group=admin_group,
            joined_at=timezone.now(),
        )


def reverse_func(apps, schema_editor):
    """ロールバック処理（マイグレーションを戻す時）"""
    User = apps.get_model("users", "User")
    Group = apps.get_model("users", "Group")

    # 管理者ユーザーを削除
    User.objects.filter(user_id="9999").delete()

    # 作成したグループを削除 (グループに他のユーザーがいないことを前提)
    Group.objects.filter(group_id="A").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_initial_superuser, reverse_func),
    ]
