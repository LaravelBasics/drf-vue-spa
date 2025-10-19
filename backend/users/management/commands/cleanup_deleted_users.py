"""
削除済みユーザー物理削除コマンド

Usage:
    python manage.py cleanup_deleted_users
    python manage.py cleanup_deleted_users --days=180
    python manage.py cleanup_deleted_users --dry-run
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from users.services.user_service import UserService

User = get_user_model()


class Command(BaseCommand):
    help = "削除後90日経過したユーザーを物理削除"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days", type=int, default=90, help="削除後の経過日数（デフォルト: 90日）"
        )
        parser.add_argument(
            "--dry-run", action="store_true", help="テスト実行（対象件数のみ表示）"
        )

    def handle(self, *args, **options):
        days = options["days"]
        dry_run = options["dry_run"]

        if dry_run:
            threshold_date = timezone.now() - timedelta(days=days)
            count = User.all_objects.filter(deleted_at__lte=threshold_date).count()

            self.stdout.write(self.style.WARNING(f"[DRY RUN] {count}件が削除対象"))
        else:
            count = UserService.permanent_delete_old_users(days=days)
            self.stdout.write(self.style.SUCCESS(f"✅ {count}件を物理削除しました"))
