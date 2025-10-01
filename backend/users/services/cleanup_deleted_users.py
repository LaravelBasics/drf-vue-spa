from django.core.management.base import BaseCommand
from users.services.user_service import UserService


class Command(BaseCommand):
    help = '削除後90日経過したユーザーを物理削除する'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='削除後何日経過したユーザーを物理削除するか（デフォルト: 90日）'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='実際には削除せず、対象件数のみ表示'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        if dry_run:
            from django.contrib.auth import get_user_model
            from django.utils import timezone
            from datetime import timedelta
            
            User = get_user_model()
            threshold_date = timezone.now() - timedelta(days=days)
            count = User.all_objects.filter(
                deleted_at__lte=threshold_date
            ).count()
            
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] {count}件のユーザーが削除対象です'
                )
            )
        else:
            count = UserService.permanent_delete_old_users(days=days)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ {count}件のユーザーを物理削除しました'
                )
            )