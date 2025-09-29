from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import random
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'ダミーユーザーを作成します'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='作成するユーザー数（デフォルト: 10）'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        
        # 既存のユーザーを削除（注意：本番環境では使用しない）
        User.objects.all().delete()
        
        # ダミーデータ作成
        users_data = []
        
        for i in range(1, count + 1):
            # ランダムな作成日（過去30日以内）
            created_at = timezone.now() - timedelta(
                days=random.randint(0, 30)
            )
            
            user_data = {
                'username': f'user{i:03d}',  # user001, user002, ...
                'employee_id': 1000 + i,     # 1001, 1002, ...
                'is_admin': i == 1,          # 1番目だけ管理者
                'password': 'password123',
                'is_active': True,
                'created_at': created_at,
            }
            
            users_data.append(user_data)
        
        # バルク作成
        for data in users_data:
            created_at = data.pop('created_at')
            password = data.pop('password')
            
            user = User.objects.create_user(
                password=password,
                **data
            )
            # 作成日を手動で設定
            user.created_at = created_at
            user.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {count} dummy users'
            )
        )