# backend/users/management/commands/create_dummy_users.py
"""
ダミーユーザー作成コマンド

このファイルの役割:
- 開発・テスト用に大量のダミーユーザーを作成
- 日本人名でランダムに生成
- 既存ユーザーは保持（上書きしない）

使い方:
python manage.py create_dummy_users --count=100 --password=test1234
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    """ダミーユーザー作成コマンド"""
    
    help = 'ダミーユーザーを効率的に作成'
    
    LAST_NAMES = [
        '佐藤', '鈴木', '高橋', '田中', '伊藤', '渡辺', '山本', '中村', '小林', '加藤',
        '吉田', '山田', '佐々木', '山口', '松本', '井上', '木村', '林', '斎藤', '清水',
    ]
    
    FIRST_NAMES = [
        '太郎', '花子', '次郎', '美咲', '健太', '由美', '大輔', '愛', '翔太', '結衣',
        '拓也', 'さくら', '直樹', '真理', '和也', '明日香', '勇気', '優子', '浩二', '麻衣',
    ]
    
    def add_arguments(self, parser):
        """コマンドライン引数を定義"""
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='作成するユーザー数'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='test1234',
            help='デフォルトパスワード'
        )
    
    def handle(self, *args, **options):
        """ダミーユーザー作成の実行"""
        count = options['count']
        default_password = options['password']
        
        # パスワードを事前にハッシュ化（効率化）
        hashed_password = make_password(default_password)
        
        # 既存データのチェック
        existing_employee_ids = set(
            User.all_objects.values_list('employee_id', flat=True)
        )
        
        has_admin = User.objects.filter(is_admin=True, is_active=True).exists()
        
        users_to_create = []
        skipped_count = 0
        attempt = 0
        created = 0
        
        self.stdout.write('ダミーユーザー作成開始...')
        
        # ユーザー生成（最大 count * 2 回まで試行）
        while created < count and attempt < count * 2:
            attempt += 1
            
            # ランダムな名前を生成
            full_name = f'{random.choice(self.LAST_NAMES)}{random.choice(self.FIRST_NAMES)}'
            
            # 社員番号を生成（重複チェック）
            employee_id = self.generate_unique_employee_id(existing_employee_ids)
            
            if employee_id is None:
                skipped_count += 1
                continue
            
            # 作成日時（過去30日以内）
            created_at = timezone.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            
            # 最初のユーザーのみ管理者（管理者がいない場合）
            is_admin = (created == 0 and not has_admin)
            
            user = User(
                employee_id=employee_id,
                username=full_name,
                email=f'{employee_id}@example.com',
                password=hashed_password,
                is_admin=is_admin,
                is_active=True,
                created_at=created_at,
            )
            
            users_to_create.append(user)
            existing_employee_ids.add(employee_id)
            created += 1
        
        # バルク作成
        if users_to_create:
            try:
                User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                created_count = len(users_to_create)
                
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ {created_count}人作成しました')
                )
                
                if skipped_count > 0:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  {skipped_count}人スキップしました')
                    )
                
                # サンプル表示
                self.stdout.write('\n作成されたユーザー（サンプル）:')
                for user in users_to_create[:5]:
                    admin_mark = ' [管理者]' if user.is_admin else ''
                    self.stdout.write(
                        f'  - 社員番号: {user.employee_id} / 名前: {user.username}{admin_mark}'
                    )
                
                if len(users_to_create) > 5:
                    self.stdout.write(f'  ... 他 {len(users_to_create) - 5}人')
                
                self.stdout.write(f'\nログイン情報:')
                self.stdout.write(f'  社員番号: {users_to_create[0].employee_id}')
                self.stdout.write(f'  パスワード: {default_password}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'\n❌ エラー: {str(e)}')
                )
        else:
            self.stdout.write(
                self.style.WARNING('作成するユーザーがありません')
            )
    
    def generate_unique_employee_id(self, existing_ids, max_attempts=100):
        """重複しない5桁の社員番号を生成"""
        for _ in range(max_attempts):
            employee_id = str(random.randint(10000, 99999))
            if employee_id not in existing_ids:
                return employee_id
        return None


# ==================== 使用例 ====================
"""
1. 基本的な使い方（100人作成）
python manage.py create_dummy_users

2. 人数を指定
python manage.py create_dummy_users --count=500

3. 人数とパスワードを両方指定
python manage.py create_dummy_users --count=200 --password=test1234


生成されるユーザー例:
- 社員番号: 12345 / 名前: 佐藤太郎
- 社員番号: 67890 / 名前: 鈴木花子
- 社員番号: 34567 / 名前: 田中次郎 [管理者]


注意点:
- employee_id（社員番号）はユニーク制約あり
- username（表示名）はユニーク制約なし（重複OK）
- 最初のユーザーは管理者になる（既に管理者がいない場合）
- 既存ユーザーは上書きしない
"""