"""
ダミーユーザー作成コマンド(パフォーマンステスト・開発用)

Usage:
    # 100件作成(デフォルト)
    python manage.py create_dummy_users

    # 100万件作成(パフォーマンステスト)
    python manage.py create_dummy_users --count=1000000

    # 確認せずに実行
    python manage.py create_dummy_users --count=10000 --yes

Safety:
    - DEBUG=False(本番環境)では実行不可
    - 1万件以上は確認プロンプト表示
    - バッチ処理で安全に挿入
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.db.models import Max
from django.conf import settings
from datetime import timedelta
import random
import sys

User = get_user_model()


class Command(BaseCommand):
    help = "ダミーユーザーを効率的に作成(開発・テスト専用)"

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
        parser.add_argument(
            "--count",
            type=int,
            default=100,
            help="作成するユーザー数(デフォルト: 100)",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="test1234",
            help="デフォルトパスワード(デフォルト: test1234)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="バッチサイズ(デフォルト: 1000)",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="確認なしで実行",
        )

    def handle(self, *args, **options):
        # セーフティチェック: DEBUG=False では実行不可
        if not settings.DEBUG:
            self.stdout.write(
                self.style.ERROR("❌ エラー: 本番環境(DEBUG=False)では実行できません")
            )
            sys.exit(1)

        count = options["count"]
        password = options["password"]
        batch_size = options["batch_size"]
        skip_confirm = options["yes"]

        # 確認プロンプト(1万件以上)
        if count >= 10000 and not skip_confirm:
            self.stdout.write(
                self.style.WARNING(f"\n⚠️  {count:,}件のダミーユーザーを作成します")
            )
            self.stdout.write("   これには時間がかかる可能性があります。")
            confirm = input("\n続行しますか? [y/N]: ")

            if confirm.lower() != "y":
                self.stdout.write("キャンセルしました")
                sys.exit(0)

        # パスワードは1回だけハッシュ化
        hashed_password = make_password(password)

        # 既存の最大社員番号を取得
        max_id = User.all_objects.aggregate(max_id=Max("user_id"))["max_id"]
        start_id = int(max_id) + 1 if max_id and max_id.isdigit() else 1

        # 管理者が存在するか確認
        has_admin = User.objects.filter(is_admin=True, is_active=True).exists()

        # 基準時刻を1回だけ取得
        base_time = timezone.now()

        self.stdout.write(f"\nダミーユーザー作成開始...")
        self.stdout.write(f"  作成数: {count:,}件")
        self.stdout.write(f"  バッチサイズ: {batch_size:,}件")

        # バッチ処理で作成
        total_created = 0
        batch = []

        for i in range(count):
            user_id = str(start_id + i)
            full_name = (
                f"{random.choice(self.LAST_NAMES)}{random.choice(self.FIRST_NAMES)}"
            )

            created_at = base_time - timedelta(
                days=random.randint(0, 365),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            is_admin = i == 0 and not has_admin

            user = User(
                user_id=user_id,
                username=full_name,
                email=f"{user_id}@example.com",
                password=hashed_password,
                is_admin=is_admin,
                is_active=True,
                created_at=created_at,
            )

            batch.append(user)

            # バッチサイズに達したら挿入
            if len(batch) >= batch_size:
                try:
                    User.objects.bulk_create(batch, ignore_conflicts=True)
                    total_created += len(batch)

                    # 進捗表示
                    progress = (total_created / count) * 100
                    self.stdout.write(
                        f"\r  進捗: {total_created:,}/{count:,}件 ({progress:.1f}%)",
                        ending="",
                    )
                    self.stdout.flush()

                    batch = []

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"\n❌ エラー: {str(e)}"))
                    sys.exit(1)

        # 残りを挿入
        if batch:
            try:
                User.objects.bulk_create(batch, ignore_conflicts=True)
                total_created += len(batch)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"\n❌ エラー: {str(e)}"))
                sys.exit(1)

        # 完了メッセージ
        self.stdout.write(
            f"\n\n{self.style.SUCCESS(f'✅ {total_created:,}件作成しました')}"
        )

        # サンプル表示
        sample_users = User.objects.filter(user_id=start_id).order_by("user_id")[:5]

        self.stdout.write("\n作成されたユーザー(サンプル):")
        for user in sample_users:
            admin_mark = " [管理者]" if user.is_admin else ""
            self.stdout.write(
                f"  - 社員番号: {user.user_id} / 名前: {user.username}{admin_mark}"
            )

        if total_created > 5:
            self.stdout.write(f"  ... 他 {total_created - 5:,}人")

        self.stdout.write(f"\nログイン情報:")
        self.stdout.write(f"  社員番号: {start_id}")
        self.stdout.write(f"  パスワード: {password}")

        # パフォーマンステスト用の情報
        if count >= 10000:
            self.stdout.write(
                f"\n{self.style.WARNING('💡 パフォーマンステストのヒント:')}"
            )
            self.stdout.write(f"  - インデックス効果: user_id で検索してみてください")
            self.stdout.write(
                f"  - ページネーション: 1000件/ページで試してみてください"
            )
            self.stdout.write(
                f"  - 複合検索: is_admin + is_active で絞り込んでみてください"
            )
