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
    """Django管理コマンド"""
    
    help = 'ダミーユーザーを効率的に作成（既存ユーザーは保持）'
    
    # ==================== 日本人名リスト ====================
    
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
    
    # ==================== コマンドライン引数 ====================
    
    def add_arguments(self, parser):
        """
        コマンドライン引数を定義
        
        --count: 作成するユーザー数
        --password: デフォルトパスワード
        """
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
            help='デフォルトパスワード（デフォルト: test1234）'
        )
    
    # ==================== メイン処理 ====================
    
    def handle(self, *args, **options):
        """
        ダミーユーザー作成の実行処理
        
        処理の流れ:
        1. コマンドライン引数を取得
        2. パスワードをハッシュ化（1回だけ）
        3. 既存の社員番号・ユーザー名を取得
        4. ランダムにユーザーを生成
        5. バルク作成（一括登録）
        """
        count = options['count']
        default_password = options['password']
        
        # パスワードを事前にハッシュ化（効率化のため1回だけ）
        hashed_password = make_password(default_password)
        
        # ==================== 既存データのチェック ====================
        
        # 既存の社員番号を取得（重複を避ける）
        # employee_id = 認証ID（ユニーク制約あり）
        existing_employee_ids = set(
            User.all_objects.values_list('employee_id', flat=True)
            .filter(employee_id__isnull=False)
        )
        
        # 既存のユーザー名を取得（参考程度・ユニーク制約なし）
        # username = 表示名（重複OK）
        existing_usernames = set(
            User.all_objects.values_list('username', flat=True)
            .filter(username__isnull=False)
        )
        
        # 管理者が存在するかチェック
        has_admin = User.objects.filter(is_admin=True, is_active=True).exists()
        
        # ==================== ユーザー生成 ====================
        
        users_to_create = []  # 作成するユーザーのリスト
        skipped_count = 0     # スキップした件数
        
        self.stdout.write('ダミーユーザー作成開始...')
        
        attempt = 0  # 試行回数
        created = 0  # 作成成功数
        
        # 無限ループ防止のため最大 count * 2 回まで試行
        while created < count and attempt < count * 2:
            attempt += 1
            
            # ① 日本人名をランダム生成
            last_name = random.choice(self.LAST_NAMES)
            first_name = random.choice(self.FIRST_NAMES)
            full_name = f'{last_name}{first_name}'
            
            # ② ユーザー名（表示名・ユニーク制約なし）
            username = full_name
            
            # ③ 社員番号（認証ID・ユニーク制約あり）
            # 5桁のランダムな数字（10000～99999）
            employee_id = self.generate_unique_employee_id(existing_employee_ids)
            
            if employee_id is None:
                # 重複が解決できない場合はスキップ
                skipped_count += 1
                continue
            
            # ④ ランダムな作成日（過去30日以内）
            created_at = timezone.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            
            # ⑤ 最初のユーザーのみ管理者（管理者がいない場合）
            is_admin = (created == 0 and not has_admin)
            
            # ⑥ ユーザーオブジェクト作成
            user = User(
                employee_id=employee_id,        # ← 認証ID（ユニーク）
                username=username,              # ← 表示名（重複OK）
                email=f'{employee_id}@example.com',
                password=hashed_password,       # ← 事前にハッシュ化済み
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
        
        # ==================== バルク作成（一括登録） ====================
        
        if users_to_create:
            try:
                # bulk_create = 一括でデータベースに登録（高速）
                # ignore_conflicts=True = 重複エラーをスキップ
                User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                created_count = len(users_to_create)
                
                # 成功メッセージ
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✅ {created_count}人のダミーユーザーを作成しました'
                    )
                )
                
                # スキップした件数を表示
                if skipped_count > 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  {skipped_count}人をスキップしました（重複回避）'
                        )
                    )
                
                # ==================== 作成結果の表示 ====================
                
                self.stdout.write('\n作成されたユーザー（サンプル）:')
                for user in users_to_create[:5]:
                    self.stdout.write(
                        f'  - 社員番号: {user.employee_id} / 名前: {user.username}'
                        + (' [管理者]' if user.is_admin else '')
                    )
                
                if len(users_to_create) > 5:
                    self.stdout.write(f'  ... 他 {len(users_to_create) - 5}人')
                
                # ログイン情報の表示
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
    
    # ==================== ヘルパーメソッド ====================
    
    def generate_unique_employee_id(self, existing_ids, max_attempts=100):
        """
        重複しない5桁の社員番号を生成
        
        引数:
            existing_ids: 既存の社員番号のセット
            max_attempts: 最大試行回数
        
        戻り値:
            str: 重複しない社員番号
            None: max_attempts 回試行しても重複した場合
        
        仕組み:
        1. 10000～99999 のランダムな5桁の数値を生成
        2. 既存IDと重複していないかチェック
        3. 重複していなければ返す
        4. 最大100回まで試行
        """
        for _ in range(max_attempts):
            # 10000～99999 のランダムな5桁の数値
            employee_id = str(random.randint(10000, 99999))
            
            if employee_id not in existing_ids:
                return employee_id
        
        # max_attempts 回試行しても重複した場合は None
        return None


# ==================== 使用例 ====================
"""
1. 基本的な使い方（100人作成）
python manage.py create_dummy_users

2. 人数を指定
python manage.py create_dummy_users --count=500

3. パスワードを指定
python manage.py create_dummy_users --count=100 --password=mypassword

4. 人数とパスワードを両方指定
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