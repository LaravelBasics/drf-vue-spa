# backend/users/management/commands/cleanup_deleted_users.py
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
            
            # 対象ユーザーを表示
            users = User.all_objects.filter(
                deleted_at__lte=threshold_date
            )
            count = users.count()
            
            self.stdout.write(
                self.style.WARNING(
                    f'\n[DRY RUN] {count}件のユーザーが削除対象です'
                )
            )
            
            if count > 0:
                self.stdout.write('\n削除対象ユーザー（最大10件）:')
                for user in users[:10]:
                    self.stdout.write(
                        f'  - 社員番号: {user.employee_id} / 名前: {user.username} '
                        f'/ 削除日: {user.deleted_at.strftime("%Y-%m-%d")}'
                    )
                
                if count > 10:
                    self.stdout.write(f'  ... 他 {count - 10}人')
        else:
            count = UserService.permanent_delete_old_users(days=days)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ {count}件のユーザーを物理削除しました'
                )
            )