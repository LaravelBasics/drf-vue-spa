# backend/users/management/commands/create_dummy_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'ダミーユーザーを効率的に作成（既存ユーザーは保持）'
    
    # 日本人の名字・名前リスト
    LAST_NAMES = [
        '佐藤', '鈴木', '高橋', '田中', '伊藤', '渡辺', '山本', '中村', '小林', '加藤',
        '吉田', '山田', '佐々木', '山口', '松本', '井上', '木村', '林', '斎藤', '清水',
        '森', '池田', '橋本', '山崎', '阿部', '石川', '中島', '前田', '藤田', '後藤',
    ]
    
    FIRST_NAMES = [
        '太郎', '花子', '次郎', '美咲', '健太', '由美', '大輔', '愛', '翔太', '結衣',
        '拓也', 'さくら', '直樹', '真理', '和也', '明日香', '勇気', '優子', '浩二', '麻衣',
        '正樹', '彩', '隆', '千鶴', '誠', '美穂', '修', '奈々', '剛', '恵',
    ]
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='作成するユーザー数（デフォルト: 100）'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='test1234',
            help='デフォルトパスワード（デフォルト: password123）'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        default_password = options['password']
        
        # パスワードを事前にハッシュ化（1回だけ）
        hashed_password = make_password(default_password)
        
        # 既存の社員番号を取得
        existing_employee_ids = set(
            User.all_objects.values_list('employee_id', flat=True)
            .filter(employee_id__isnull=False)
        )
        
        # 既存のユーザー名を取得（重複チェック用・ユニーク制約なしなので参考程度）
        existing_usernames = set(
            User.all_objects.values_list('username', flat=True)
            .filter(username__isnull=False)
        )
        
        # 管理者が存在するかチェック
        has_admin = User.objects.filter(is_admin=True, is_active=True).exists()
        
        users_to_create = []
        skipped_count = 0
        
        self.stdout.write('ダミーユーザー作成開始...')
        
        attempt = 0
        created = 0
        
        while created < count and attempt < count * 2:  # 無限ループ防止
            attempt += 1
            
            # 日本人名生成
            last_name = random.choice(self.LAST_NAMES)
            first_name = random.choice(self.FIRST_NAMES)
            full_name = f'{last_name}{first_name}'
            
            # ユーザー名: 日本語のフルネーム（ユニーク制約なし）
            username = full_name
            
            # 重複しない5桁の社員番号生成（認証ID・ユニーク制約あり）
            employee_id = self.generate_unique_employee_id(existing_employee_ids)
            
            if employee_id is None:
                # 重複が解決できない場合はスキップ
                skipped_count += 1
                continue
            
            # ランダムな作成日（過去30日以内）
            created_at = timezone.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            
            # 最初のユーザーのみ管理者（既に管理者がいない場合）
            is_admin = (created == 0 and not has_admin)
            
            # ユーザーオブジェクト作成
            user = User(
                employee_id=employee_id,  # ← 認証ID（ユニーク制約あり）
                username=username,         # ← 表示名（ユニーク制約なし）
                email=f'{employee_id}@example.com',  # 仮メール
                password=hashed_password,
                is_admin=is_admin,
                is_active=True,
                is_staff=False,
                is_superuser=False,
                created_at=created_at,
            )
            
            users_to_create.append(user)
            existing_employee_ids.add(employee_id)
            existing_usernames.add(username)
            created += 1
        
        # バルク作成
        if users_to_create:
            try:
                User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                created_count = len(users_to_create)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✅ {created_count}人のダミーユーザーを作成しました'
                    )
                )
                
                if skipped_count > 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  {skipped_count}人をスキップしました（重複回避）'
                        )
                    )
                
                # 作成されたユーザーを表示
                self.stdout.write('\n作成されたユーザー（サンプル）:')
                for user in users_to_create[:5]:
                    self.stdout.write(
                        f'  - 社員番号: {user.employee_id} / 名前: {user.username}'
                        + (' [管理者]' if user.is_admin else '')
                    )
                
                if len(users_to_create) > 5:
                    self.stdout.write(f'  ... 他 {len(users_to_create) - 5}人')
                
                self.stdout.write(f'\nログイン情報:')
                self.stdout.write(f'  社員番号: {users_to_create[0].employee_id}')
                self.stdout.write(f'  パスワード: {default_password}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'\n❌ エラーが発生しました: {str(e)}')
                )
        else:
            self.stdout.write(
                self.style.WARNING('作成するユーザーがありません')
            )
    
    def generate_unique_employee_id(self, existing_ids, max_attempts=100):
        """
        重複しない5桁の社員番号を生成
        重複が続く場合は None を返す（スキップさせる）
        """
        for _ in range(max_attempts):
            # 10000～99999 のランダムな5桁の数値
            employee_id = str(random.randint(10000, 99999))
            
            if employee_id not in existing_ids:
                return employee_id
        
        # max_attempts回試行しても重複した場合は None
        return None