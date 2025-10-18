# backend/users/models.py
"""
カスタムユーザーモデル

このファイルの役割:
- ユーザーのデータ構造を定義
- 社員番号（employee_id）でログインする仕組み
- 論理削除（削除してもデータは残る）
- カスタムマネージャー（削除済みの扱い）

なぜカスタムユーザーモデルが必要？:
- Django標準は username でログインするが、employee_id でログインしたい
- 論理削除機能を追加したい
- 管理者権限（is_admin）を独自に管理したい
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


# ==================== マネージャー（データ取得方法をカスタマイズ） ====================

class CustomUserManager(BaseUserManager):
    """
    カスタムユーザーマネージャー（論理削除対応）
    
    マネージャーとは:
    - モデルのデータを取得する方法を定義
    - User.objects.all() の「objects」がマネージャー
    
    このマネージャーの特徴:
    - デフォルトで削除済みユーザーを除外
    - User.objects.all() → 削除済みは含まれない
    """
    
    def get_queryset(self):
        """
        デフォルトで削除済みを除外
        
        deleted_at が NULL のユーザーのみ取得
        （deleted_at に日時が入っている = 削除済み）
        """
        return super().get_queryset().filter(deleted_at__isnull=True)
    
    def create_user(self, employee_id, password=None, **extra_fields):
        """
        通常のユーザーを作成
        
        引数:
            employee_id: 社員番号（必須）
            password: パスワード
            extra_fields: その他のフィールド（username, email など）
        
        戻り値:
            作成されたユーザー
        
        使い方:
            user = User.objects.create_user(
                employee_id='EMP001',
                password='password123',
                username='山田太郎'
            )
        """
        # 社員番号チェック
        if not employee_id:
            raise ValueError('社員番号は必須です')
        
        # デフォルト値を設定
        extra_fields.setdefault('is_active', True)   # アクティブ
        extra_fields.setdefault('is_admin', False)   # 一般ユーザー
        
        # ユーザーインスタンスを作成
        user = self.model(employee_id=employee_id, **extra_fields)
        
        # パスワードをハッシュ化して設定
        user.set_password(password)
        
        # データベースに保存
        user.save(using=self._db)
        return user
    
    def create_superuser(self, employee_id, password=None, **extra_fields):
        """
        スーパーユーザー（最高権限）を作成
        
        スーパーユーザーとは:
        - 管理画面にログインできる
        - すべての権限を持つ
        - 初期セットアップで1人作成する
        
        使い方:
            python manage.py createsuperuser
        """
        # スーパーユーザーは管理者権限を強制
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)       # 管理画面ログインOK
        extra_fields.setdefault('is_superuser', True)   # 全権限
        
        # チェック
        if extra_fields.get('is_admin') is not True:
            raise ValueError('スーパーユーザーは is_admin=True である必要があります')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('スーパーユーザーは is_staff=True である必要があります')
        
        # 通常のユーザー作成処理を呼び出し
        return self.create_user(employee_id, password, **extra_fields)


class AllObjectsManager(BaseUserManager):
    """
    全レコード取得用マネージャー（削除済みも含む）
    
    このマネージャーの特徴:
    - 削除済みも含めて全件取得
    - User.all_objects.all() → 削除済みも含まれる
    
    使い分け:
    - User.objects.all() → 削除済み除外
    - User.all_objects.all() → 削除済み含む
    """
    
    def get_queryset(self):
        """削除済みも含めて全件取得"""
        return super().get_queryset()


# ==================== ユーザーモデル ====================

class User(AbstractBaseUser, PermissionsMixin):
    """
    カスタムユーザーモデル
    
    継承クラス:
    - AbstractBaseUser: パスワード管理、最終ログイン日時などの基本機能
    - PermissionsMixin: 権限管理機能（is_superuser, groups など）
    
    特徴:
    1. employee_id（社員番号）でログイン
    2. username はユニーク制約なしの表示名
    3. 論理削除対応（deleted_at フィールド）
    4. email は任意
    """
    
    # ==================== 認証フィールド ====================
    
    employee_id = models.CharField(
        '社員番号',
        max_length=20,          # 最大20文字
        unique=True,            # 重複不可（ログインIDとして使用）
        db_index=True,          # 検索高速化のためインデックス作成
        help_text='ログイン認証に使用する一意の社員番号'
    )
    
    # ==================== 表示名・個人情報 ====================
    
    username = models.CharField(
        'ユーザー名',
        max_length=50,
        blank=True,             # 空文字列OK
        null=True,              # NULL OK
        help_text='表示用のユーザー名（ユニーク制約なし）'
    )
    
    email = models.EmailField(
        'メールアドレス',
        max_length=255,
        blank=True,
        null=True,
        help_text='メールアドレス（任意）'
    )
    
    # ==================== 権限・ステータス ====================
    
    is_admin = models.BooleanField(
        '管理者',
        default=False,
        help_text='管理者権限を持つかどうか'
    )
    
    is_staff = models.BooleanField(
        'スタッフ',
        default=False,
        help_text='Django管理サイト（/admin/）にアクセスできるかどうか'
    )
    
    is_active = models.BooleanField(
        'アクティブ',
        default=True,
        help_text='アカウントが有効かどうか（False = 無効化、ログイン不可）'
    )
    
    # ==================== タイムスタンプ ====================
    
    created_at = models.DateTimeField(
        '作成日時',
        default=timezone.now    # 作成時に自動で現在日時をセット
    )
    
    updated_at = models.DateTimeField(
        '更新日時',
        auto_now=True           # 保存時に自動で現在日時に更新
    )
    
    deleted_at = models.DateTimeField(
        '削除日時',
        blank=True,
        null=True,              # NULL = 削除されていない
        help_text='論理削除された日時（NULL = 未削除）'
    )
    
    # ==================== Django認証設定 ====================
    
    # ログイン時に使用するフィールド（通常は username だが employee_id に変更）
    USERNAME_FIELD = 'employee_id'
    
    # createsuperuser コマンドで追加で入力を求めるフィールド
    REQUIRED_FIELDS = ['username']
    
    # ==================== マネージャー ====================
    
    # デフォルトマネージャー（削除済み除外）
    objects = CustomUserManager()
    
    # 全件取得用マネージャー（削除済みも含む）
    all_objects = AllObjectsManager()
    
    # ==================== メタ情報 ====================
    
    class Meta:
        # データベーステーブル名
        db_table = 'users'
        
        # 管理画面での表示名
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'
        
        # デフォルトの並び順（新しい順）
        ordering = ['-created_at']
        
        # インデックス（検索高速化）
        indexes = [
            models.Index(fields=['employee_id']),  # 社員番号で検索
            models.Index(fields=['is_active']),    # アクティブステータスで絞り込み
            models.Index(fields=['deleted_at']),   # 削除済み判定
            models.Index(fields=['is_admin', 'is_active']),  # 管理者検索用
            models.Index(fields=['-created_at']),            # 並び替え用
        ]
    
    # ==================== 文字列表現 ====================
    
    def __str__(self):
        """
        オブジェクトを文字列で表示
        
        使われる場面:
        - 管理画面のユーザー一覧
        - print(user) の出力
        - ログ出力
        
        出力例:
        "EMP001 (山田太郎)"
        "EMP002 (名前未設定)"
        """
        return f"{self.employee_id} ({self.username or '名前未設定'})"
    
    # ==================== カスタムメソッド ====================
    
    def soft_delete(self):
        """
        論理削除（データは残る）
        
        やること:
        1. deleted_at に現在日時をセット
        2. is_active を False にする（ログイン不可）
        
        物理削除との違い:
        - 物理削除: データベースから完全に消える（復元不可）
        - 論理削除: データは残る（復元可能）
        
        使い方:
            user.soft_delete()
        """
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()
    
    def restore(self):
        """
        復元（削除を取り消し）
        
        やること:
        1. deleted_at を NULL にする
        2. is_active を True にする（ログイン可能）
        
        使い方:
            user.restore()
        """
        self.deleted_at = None
        self.is_active = True
        self.save()
    
    @property
    def display_name(self):
        """
        表示用の名前を取得
        
        @property とは:
        - メソッドをフィールドのように扱える
        - user.display_name で取得できる（括弧不要）
        
        ロジック:
        - username があればそれを返す
        - なければ employee_id を返す
        
        使い方:
            user.display_name → "山田太郎" or "EMP001"
        """
        return self.username or self.employee_id
    
    def has_perm(self, perm, obj=None):
        """
        権限チェック
        
        Django の権限システムで使用される
        
        ロジック:
        - is_admin=True → すべての権限を持つ
        - is_admin=False → 個別の権限をチェック
        
        引数:
            perm: 権限の識別子（例: 'users.add_user'）
            obj: 対象オブジェクト（通常は None）
        
        戻り値:
            True: 権限あり
            False: 権限なし
        """
        return self.is_admin or super().has_perm(perm, obj)
    
    def has_module_perms(self, app_label):
        """
        アプリケーションの権限チェック
        
        Django の権限システムで使用される
        
        ロジック:
        - is_admin=True → すべてのアプリにアクセスOK
        - is_admin=False → 個別の権限をチェック
        
        引数:
            app_label: アプリ名（例: 'users', 'products'）
        
        戻り値:
            True: アクセス可能
            False: アクセス不可
        """
        return self.is_admin or super().has_module_perms(app_label)


# ==================== マネージャーの使い分け ====================
"""
CustomUserManager vs AllObjectsManager

1. 通常の操作（削除済み除外）
   User.objects.all()              → 削除済みを除外
   User.objects.get(id=1)          → 削除済みなら DoesNotExist
   User.objects.filter(is_admin=True)  → 削除済み除外 + 管理者のみ

2. 削除済みも含む操作
   User.all_objects.all()          → 削除済みも含む
   User.all_objects.get(id=1)      → 削除済みでも取得
   User.all_objects.filter(deleted_at__isnull=False)  → 削除済みのみ


使用例:

# 削除済み除外（通常）
active_users = User.objects.all()

# 削除済みも含む（管理画面・統計など）
all_users = User.all_objects.all()

# 削除済みのみ取得
deleted_users = User.all_objects.filter(deleted_at__isnull=False)
"""


# ==================== 論理削除の仕組み ====================
"""
論理削除の流れ:

1. 削除リクエスト
   DELETE /api/users/1/

2. views.py
   UserService.delete_user(user)

3. user_service.py
   user.soft_delete()

4. models.py（このファイル）
   self.deleted_at = timezone.now()
   self.is_active = False
   self.save()

5. データベース
   UPDATE users SET deleted_at='2025-01-15 10:00:00', is_active=0 WHERE id=1

6. 以降の取得
   User.objects.all() → このユーザーは含まれない
   User.all_objects.all() → このユーザーも含まれる


復元の流れ:

1. 復元リクエスト
   POST /api/users/1/restore/

2. views.py
   UserService.restore_user(1)

3. user_service.py
   user.restore()

4. models.py
   self.deleted_at = None
   self.is_active = True
   self.save()

5. データベース
   UPDATE users SET deleted_at=NULL, is_active=1 WHERE id=1

6. 以降の取得
   User.objects.all() → このユーザーが含まれる
"""


# ==================== フィールドの役割まとめ ====================
"""
認証関連:
- employee_id: ログインID（社員番号）
- password: パスワード（ハッシュ化されて保存）

表示名:
- username: 表示用の名前（任意）
- email: メールアドレス（任意）

権限:
- is_admin: 管理者権限（ユーザー管理などができる）
- is_staff: 管理画面アクセス権
- is_superuser: 最高権限（すべての権限）
- is_active: アカウント有効フラグ

タイムスタンプ:
- created_at: 作成日時
- updated_at: 更新日時
- deleted_at: 削除日時（NULL = 未削除）


フィールドの組み合わせ:

通常の管理者:
- is_admin=True, is_active=True, deleted_at=NULL

通常の一般ユーザー:
- is_admin=False, is_active=True, deleted_at=NULL

無効化されたユーザー:
- is_active=False, deleted_at=NULL

削除済みユーザー:
- is_active=False, deleted_at='2025-01-15 10:00:00'

スーパーユーザー:
- is_admin=True, is_staff=True, is_superuser=True
"""


# ==================== データベーススキーマ ====================
"""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id VARCHAR(20) NOT NULL UNIQUE,
    username VARCHAR(50),
    email VARCHAR(255),
    password VARCHAR(128) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT 0,
    is_staff BOOLEAN NOT NULL DEFAULT 0,
    is_superuser BOOLEAN NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    deleted_at DATETIME,
    last_login DATETIME
);

CREATE INDEX idx_employee_id ON users(employee_id);
CREATE INDEX idx_is_active ON users(is_active);
CREATE INDEX idx_deleted_at ON users(deleted_at);
"""


# ==================== モデルの使用例 ====================
"""
1. ユーザー作成
user = User.objects.create_user(
    employee_id='EMP001',
    password='password123',
    username='山田太郎',
    email='yamada@example.com',
    is_admin=False
)

2. ユーザー取得
user = User.objects.get(employee_id='EMP001')
users = User.objects.filter(is_admin=True)
all_users = User.all_objects.all()  # 削除済みも含む

3. ユーザー更新
user.username = '山田次郎'
user.save()

4. 論理削除
user.soft_delete()

5. 復元
user.restore()

6. 物理削除（非推奨）
user.delete()  # データベースから完全に削除

7. パスワード変更
user.set_password('newpassword123')
user.save()

8. パスワード確認
if user.check_password('password123'):
    print('パスワード正しい')

9. 表示名取得
print(user.display_name)  # "山田太郎" or "EMP001"

10. 権限チェック
if user.is_admin:
    print('管理者です')
"""