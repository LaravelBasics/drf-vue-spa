"""
ダミーユーザー作成コマンド

Usage:
    python manage.py create_dummy_users --count=100 --password=test1234
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.db.models import Max
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = "ダミーユーザーを効率的に作成"

    LAST_NAMES = [
        "佐藤",
        "鈴木",
        "高橋",
        "田中",
        "伊藤",
        "渡辺",
        "山本",
        "中村",
        "小林",
        "加藤",
        "吉田",
        "山田",
        "佐々木",
        "山口",
        "松本",
        "井上",
        "木村",
        "林",
        "斎藤",
        "清水",
    ]

    FIRST_NAMES = [
        "太郎",
        "花子",
        "次郎",
        "美咲",
        "健太",
        "由美",
        "大輔",
        "愛",
        "翔太",
        "結衣",
        "拓也",
        "さくら",
        "直樹",
        "真理",
        "和也",
        "明日香",
        "勇気",
        "優子",
        "浩二",
        "麻衣",
    ]

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=100, help="作成するユーザー数")
        parser.add_argument(
            "--password", type=str, default="test1234", help="デフォルトパスワード"
        )

    def handle(self, *args, **options):
        count = options["count"]
        default_password = options["password"]

        # パスワードは1回だけハッシュ化（全ユーザー共通）
        hashed_password = make_password(default_password)

        # 既存の最大社員番号を取得
        max_id = User.all_objects.aggregate(max_id=Max("employee_id"))["max_id"]
        start_id = int(max_id) + 1 if max_id and max_id.isdigit() else 1

        # 管理者が存在するか確認
        has_admin = User.objects.filter(is_admin=True, is_active=True).exists()

        # 基準時刻を1回だけ取得
        base_time = timezone.now()

        users_to_create = []

        self.stdout.write("ダミーユーザー作成開始...")

        for i in range(count):
            employee_id = str(start_id + i)
            full_name = (
                f"{random.choice(self.LAST_NAMES)}{random.choice(self.FIRST_NAMES)}"
            )

            # 基準時刻から相対的に計算
            created_at = base_time - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            is_admin = i == 0 and not has_admin

            user = User(
                employee_id=employee_id,
                username=full_name,
                email=f"{employee_id}@example.com",
                password=hashed_password,
                is_admin=is_admin,
                is_active=True,
                created_at=created_at,
            )

            users_to_create.append(user)

        if users_to_create:
            try:
                User.objects.bulk_create(users_to_create, ignore_conflicts=True)

                self.stdout.write(self.style.SUCCESS(f"\n✅ {count}人作成しました"))

                self.stdout.write("\n作成されたユーザー（サンプル）:")
                for user in users_to_create[:5]:
                    admin_mark = " [管理者]" if user.is_admin else ""
                    self.stdout.write(
                        f"  - 社員番号: {user.employee_id} / 名前: {user.username}{admin_mark}"
                    )

                if len(users_to_create) > 5:
                    self.stdout.write(f"  ... 他 {len(users_to_create) - 5}人")

                self.stdout.write(f"\nログイン情報:")
                self.stdout.write(f"  社員番号: {users_to_create[0].employee_id}")
                self.stdout.write(f"  パスワード: {default_password}")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"\n❌ エラー: {str(e)}"))
        else:
            self.stdout.write(self.style.WARNING("作成するユーザーがありません"))
