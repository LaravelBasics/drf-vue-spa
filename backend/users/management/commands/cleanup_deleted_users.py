# backend/users/management/commands/cleanup_deleted_users.py
"""
削除済みユーザーの定期削除コマンド

このファイルの役割:
- 古い削除済みユーザーをデータベースから完全削除（物理削除）
- cron や Windows タスクスケジューラで定期実行する

使い方:
# 通常実行（90日前に削除されたユーザーを物理削除）
python manage.py cleanup_deleted_users

# 日数を指定
python manage.py cleanup_deleted_users --days=180

# テスト実行（実際には削除せず、対象件数だけ表示）
python manage.py cleanup_deleted_users --dry-run
"""

from django.core.management.base import BaseCommand
from users.services.user_service import UserService


class Command(BaseCommand):
    """Django の管理コマンド"""
    
    # python manage.py help cleanup_deleted_users で表示される説明
    help = '削除後90日経過したユーザーを物理削除する'
    
    def add_arguments(self, parser):
        """
        コマンドライン引数を定義
        
        定義する引数:
        - --days: 何日前に削除されたユーザーを対象とするか
        - --dry-run: テスト実行フラグ
        """
        # --days オプション（日数指定）
        parser.add_argument(
            '--days',
            type=int,              # 整数のみ受け付ける
            default=90,            # デフォルト値
            help='削除後何日経過したユーザーを物理削除するか（デフォルト: 90日）'
        )
        
        # --dry-run オプション（テスト実行）
        parser.add_argument(
            '--dry-run',
            action='store_true',   # フラグ型（付けるとTrue）
            help='実際には削除せず、対象件数のみ表示'
        )
    
    def handle(self, *args, **options):
        """
        コマンドの実行処理
        
        引数:
            options: コマンドライン引数の辞書
                例: {'days': 90, 'dry_run': False}
        """
        # コマンドライン引数を取得
        days = options['days']
        dry_run = options['dry_run']
        
        # テスト実行の場合
        if dry_run:
            # 対象件数のみカウント（削除しない）
            from django.contrib.auth import get_user_model
            from django.utils import timezone
            from datetime import timedelta
            
            User = get_user_model()
            threshold_date = timezone.now() - timedelta(days=days)
            
            # 削除対象のユーザー件数を取得
            count = User.all_objects.filter(
                deleted_at__lte=threshold_date
            ).count()
            
            # 警告メッセージで表示（黄色）
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] {count}件のユーザーが削除対象です'
                )
            )
        
        # 本番実行の場合
        else:
            # UserService の permanent_delete_old_users を呼び出す
            count = UserService.permanent_delete_old_users(days=days)
            
            # 成功メッセージで表示（緑色）
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ {count}件のユーザーを物理削除しました'
                )
            )