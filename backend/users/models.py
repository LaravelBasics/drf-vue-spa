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

⭐ 変更点:
- employee_id の max_length を 20 → 50 に拡張
- 条件付きユニーク制約を追加（論理削除対応）
"""

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
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
            raise ValueError("社員番号は必須です")

        # デフォルト値を設定
        extra_fields.setdefault("is_active", True)  # アクティブ
        extra_fields.setdefault("is_admin", False)  # 一般ユーザー

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
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_staff", True)  # 管理画面ログインOK
        extra_fields.setdefault("is_superuser", True)  # 全権限

        # チェック
        if extra_fields.get("is_admin") is not True:
            raise ValueError("スーパーユーザーは is_admin=True である必要があります")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("スーパーユーザーは is_staff=True である必要があります")

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

    ⭐ 論理削除の仕組み:
    - employee_id はそのまま保持（履歴として重要）
    - deleted_at が NULL = アクティブ、値あり = 削除済み
    - 条件付きユニーク制約で番号の再利用が可能
    """

    # ==================== 認証フィールド ====================

    employee_id = models.CharField(
        "社員番号",
        max_length=50,  # ⭐ 20→50に拡張（論理削除で番号を保持するため余裕を持たせる）
        unique=False,  # 重複不可（ただし条件付き制約で上書きされる）
        db_index=True,  # 検索高速化のためインデックス作成
        help_text="ログイン認証に使用する一意の社員番号（論理削除時も番号をそのまま保持）",
    )

    # ==================== 表示名・個人情報 ====================

    username = models.CharField(
        "ユーザー名",
        max_length=50,
        blank=True,  # 空文字列OK
        null=True,  # NULL OK
        help_text="表示用のユーザー名（ユニーク制約なし）",
    )

    email = models.EmailField(
        "メールアドレス",
        max_length=255,
        blank=True,
        null=True,
        help_text="メールアドレス（任意）",
    )

    # ==================== 権限・ステータス ====================

    is_admin = models.BooleanField(
        "管理者", default=False, help_text="管理者権限を持つかどうか"
    )

    is_staff = models.BooleanField(
        "スタッフ",
        default=False,
        help_text="Django管理サイト（/admin/）にアクセスできるかどうか",
    )

    is_active = models.BooleanField(
        "アクティブ",
        default=True,
        help_text="アカウントが有効かどうか（False = 無効化、ログイン不可）",
    )

    # ==================== タイムスタンプ ====================

    created_at = models.DateTimeField(
        "作成日時", default=timezone.now  # 作成時に自動で現在日時をセット
    )

    updated_at = models.DateTimeField(
        "更新日時", auto_now=True  # 保存時に自動で現在日時に更新
    )

    deleted_at = models.DateTimeField(
        "削除日時",
        blank=True,
        null=True,  # NULL = 削除されていない
        help_text="論理削除された日時（NULL = 未削除）",
    )

    # ==================== Django認証設定 ====================

    # ログイン時に使用するフィールド（通常は username だが employee_id に変更）
    USERNAME_FIELD = "employee_id"

    # createsuperuser コマンドで追加で入力を求めるフィールド
    REQUIRED_FIELDS = ["username"]

    # ==================== マネージャー ====================

    # デフォルトマネージャー（削除済み除外）
    objects = CustomUserManager()

    # 全件取得用マネージャー（削除済みも含む）
    all_objects = AllObjectsManager()

    # ==================== メタ情報 ====================

    class Meta:
        # データベーステーブル名
        db_table = "users"

        # 管理画面での表示名
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー"

        # デフォルトの並び順（新しい順）
        ordering = ["-created_at"]

        # ⭐ 条件付きユニーク制約（論理削除対応）
        # deleted_at が NULL（アクティブ）の場合のみ employee_id を一意にする
        # これにより削除済みユーザーの社員番号を再利用できる
        constraints = [
            models.UniqueConstraint(
                fields=["employee_id"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_active_employee_id",
            )
        ]

        # インデックス（検索高速化）
        indexes = [
            models.Index(fields=["employee_id"]),  # 社員番号で検索
            models.Index(fields=["is_active"]),  # アクティブステータスで絞り込み
            models.Index(fields=["deleted_at"]),  # 削除済み判定
            models.Index(fields=["is_admin", "is_active"]),  # 管理者検索用
            models.Index(fields=["-created_at"]),  # 並び替え用
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
        "EMP001 (山田太郎) [削除済み]"  ⭐ 削除済み表示を追加
        """
        status = " [削除済み]" if self.deleted_at else ""
        return f"{self.employee_id} ({self.username or '名前未設定'}){status}"

    # ==================== カスタムメソッド ====================

    def soft_delete(self):
        """
        論理削除（データは残る）

        やること:
        1. deleted_at に現在日時をセット
        2. is_active を False にする（ログイン不可）

        ⭐ 重要: employee_id は変更しない！
        - deleted_at を設定することで条件付きユニーク制約から外れる
        - 履歴として社員番号をそのまま保持
        - 後で同じ社員番号を別のユーザーに割り当て可能

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


# ==================== 論理削除の仕組み（条件付きユニーク制約版） ====================
"""
⭐ 社員番号の再利用が可能な仕組み:

パターン1: 削除→再利用
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. ユーザーA作成
   id: 1
   employee_id: "1000"
   deleted_at: NULL
   → ユニーク制約OK（条件を満たす）

2. ユーザーAを論理削除
   id: 1
   employee_id: "1000" ← そのまま保持！
   deleted_at: "2025-01-15 10:00:00"
   → ユニーク制約から外れる（deleted_at が NULL じゃない）

3. 新しいユーザーBを作成（同じ社員番号）
   id: 2
   employee_id: "1000" ← 再利用OK！
   deleted_at: NULL
   → ユニーク制約OK（条件を満たす）

4. 履歴確認
   User.all_objects.filter(employee_id="1000")
   → ユーザーA（削除済み）とユーザーB（アクティブ）の2件

5. 通常の検索
   User.objects.filter(employee_id="1000")
   → ユーザーB のみ（削除済みは除外）


パターン2: 削除済みユーザーの検索
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# アクティブなユーザーのみ
User.objects.filter(employee_id="1000")
→ ユーザーB のみ

# 削除済みも含めて検索
User.all_objects.filter(employee_id="1000")
→ ユーザーA（削除済み）とユーザーB（アクティブ）の2件

# 削除済みのみ
User.all_objects.filter(employee_id="1000", deleted_at__isnull=False)
→ ユーザーA のみ


パターン3: 監査・履歴追跡
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 「社員番号1000は過去に誰が使っていた？」
User.all_objects.filter(employee_id="1000").order_by('created_at')
→ 時系列で全員表示

# 「2024年に社員番号1000だった人は？」
User.all_objects.filter(
    employee_id="1000",
    created_at__year=2024
)

# 「現在の社員番号1000は？」
User.objects.get(employee_id="1000")
→ アクティブなユーザーのみ取得


条件付きユニーク制約のSQL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CREATE UNIQUE INDEX unique_active_employee_id
ON users(employee_id)
WHERE deleted_at IS NULL;

この制約により:
- deleted_at が NULL のレコードのみ employee_id がユニーク
- deleted_at に値があるレコードは制約の対象外
- 同じ employee_id でも deleted_at が NULL かどうかで別レコード扱い
"""


# ==================== フィールドの役割まとめ ====================
"""
認証関連:
- employee_id: ログインID（社員番号）max_length=50 ⭐
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
- deleted_at: 削除日時（NULL = 未削除）⭐


フィールドの組み合わせ:

通常の管理者:
- is_admin=True, is_active=True, deleted_at=NULL

通常の一般ユーザー:
- is_admin=False, is_active=True, deleted_at=NULL

無効化されたユーザー:
- is_active=False, deleted_at=NULL

削除済みユーザー:
- employee_id="1000" ← そのまま保持 ⭐
- is_active=False, deleted_at='2025-01-15 10:00:00'

スーパーユーザー:
- is_admin=True, is_staff=True, is_superuser=True
"""


# ==================== マイグレーション手順 ====================
"""
既存のプロジェクトで変更を適用する手順:

1. models.py の employee_id を max_length=50 に変更（このファイル）

2. マイグレーションファイル作成
   python manage.py makemigrations

3. マイグレーション実行
   python manage.py migrate

4. 既存データは自動的に保持される
   - employee_id: "EMP001" → "EMP001" のまま
   - 新しく50文字まで入力可能になる

5. 他のファイルも更新
   - accounts/serializers.py の max_length を 50 に
   - users/serializers.py の max_length を 50 に
"""

# ==================== 解説 ====================
"""
問題の原因:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. フィールド定義の unique=True
   → データベースに UNIQUE 制約が作られる
   → 削除済みでも重複エラーになる

2. Meta.constraints の条件付き制約
   → deleted_at が NULL の時だけユニーク
   → これが正しい動作

3. 両方あると unique=True が優先される
   → 条件付き制約が無視される
   → 削除済みでも重複エラー ← 今回のエラー


修正内容:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ 削除前:
employee_id = models.CharField(
    max_length=50,
    unique=True,  # フィールドレベルの制約
)

✅ 修正後:
employee_id = models.CharField(
    max_length=50,
    unique=False,  # フィールドレベルの制約を無効化
    db_index=True,  # 検索用インデックスは残す
)

class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=['employee_id'],
            condition=models.Q(deleted_at__isnull=True),
            name='unique_active_employee_id'
        )
    ]
"""
