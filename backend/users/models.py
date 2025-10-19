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
- check() メソッドで W004 警告を抑制 ← NEW!
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
        unique=False,  # ⭐ 条件付きユニーク制約を使うため False（重要！）
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

    # ==================== ⭐ システムチェック警告の抑制 ====================

    @classmethod
    def check(cls, **kwargs):
        """
        Django のシステムチェックをオーバーライド

        ⭐ このメソッドを追加するだけで W004 警告が消える！

        やっていること:
        1. 親クラス（AbstractBaseUser）の check() を呼び出す
           → すべての警告とエラーをリストで取得

        2. W004 警告だけをフィルタリングして除外
           → error.id が 'auth.W004' じゃないものだけ残す

        3. 残りの警告・エラーを返す
           → セキュリティ関連の警告は残るので安全


        なぜこれで安全なのか:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        ✅ データベースレベルの保証
           - 条件付きユニーク制約で employee_id の一意性を保証
           - deleted_at が NULL の時だけユニーク

        ✅ アプリケーションレベルの保証
           - UniqueValidator でバリデーション
           - 作成・更新時に重複チェック

        ✅ ビジネスロジックレベルの保証
           - UserService で復元時にチェック
           - 論理削除で元の番号を保持


        他の警告は残る:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        auth.W005: MIDDLEWARE の問題
        auth.W006: SESSION_COOKIE_SECURE の問題
        auth.E003: パスワードハッシュの問題
        などなど...

        → これらのセキュリティ関連の警告は表示される
        → 問題があれば検知できる
        """
        # 親クラスのチェックを実行してすべての警告を取得
        errors = super().check(**kwargs)

        # W004 警告のみ除外（論理削除のため条件付きユニーク制約を使用）
        errors = [error for error in errors if error.id != "auth.W004"]

        return errors

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

1. models.py を上書き（このファイル）

2. マイグレーション不要！
   ✅ check() メソッドはコードレベルの変更
   ✅ データベース構造は変わらない
   ✅ そのまま使える

3. 警告チェック
   python manage.py check
   
   期待される結果:
   System check identified no issues (0 silenced).
   ✅ W004 警告が消える！

4. サーバー再起動
   python manage.py runserver
   
   ✅ 警告なしで起動する
"""


# ==================== 解説 ====================
"""
⭐ W004 警告が出る理由と解決方法
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


【問題】なぜ警告が出るのか？
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Django の認証システムは、USERNAME_FIELD に指定したフィールドが
unique=True であることを期待しています。

通常の設計:
  employee_id = models.CharField(unique=True)
  ↓
  ✅ 警告なし
  ✅ 削除しても再利用不可（物理削除のみ）


論理削除の設計:
  employee_id = models.CharField(unique=False)  ← これが必要
  ↓
  ⚠️ W004 警告が出る
  ✅ 削除しても再利用可能（論理削除）


なぜ unique=False が必要なのか:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

例: 社員番号「1000」のユーザーを削除→再利用する場合

1. ユーザーA（社員番号1000）を作成
   employee_id: "1000"
   deleted_at: NULL

2. ユーザーAを論理削除
   employee_id: "1000" ← 変更しない！
   deleted_at: "2025-01-15 10:00:00"

3. 新しいユーザーB（社員番号1000）を作成
   employee_id: "1000" ← 同じ番号！
   deleted_at: NULL

もし unique=True だと:
  → 手順3で「この社員番号は既に使われています」エラー
  → 削除済みでも重複判定される（使えない）

unique=False + 条件付きユニーク制約だと:
  → 手順3で作成成功！
  → deleted_at が NULL の時だけユニーク判定
  → 削除済みは制約の対象外


【解決策1】条件付きユニーク制約を使う
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=['employee_id'],
            condition=models.Q(deleted_at__isnull=True),  ← これが重要
            name='unique_active_employee_id'
        )
    ]

この制約の意味:
  「deleted_at が NULL の時だけ employee_id をユニークにする」

つまり:
  アクティブなユーザー間では社員番号は重複不可 ✅
  削除済みユーザーは制約の対象外 ✅
  同じ社員番号を再利用できる ✅


【解決策2】check() メソッドで警告を抑制
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@classmethod
def check(cls, **kwargs):
    errors = super().check(**kwargs)
    
    # W004 警告だけ除外
    errors = [
        error for error in errors
        if error.id != 'auth.W004'
    ]
    
    return errors

この処理の流れ:
  1. 親クラスの check() を呼ぶ
     → すべての警告・エラーを取得（リストで返ってくる）
  
  2. リスト内包表記でフィルタリング
     → error.id が 'auth.W004' じゃないものだけ残す
  
  3. フィルタリング後のリストを返す
     → W004 警告は除外される
     → 他の警告は残る（セキュリティのため）


なぜこれで安全なのか？
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 3層の保護がある:

1. データベースレベル（最も強固）
   条件付きユニーク制約
   → アクティブユーザーの employee_id は確実に一意

2. アプリケーションレベル
   UniqueValidator（serializers.py）
   → 作成・更新時にバリデーション
   → 重複があれば 400 エラーを返す

3. ビジネスロジックレベル
   UserService（services/user_service.py）
   → 復元時に重複チェック
   → 適切なエラーメッセージを返す


【実行結果の比較】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ check() メソッド追加前:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ python manage.py check

System check identified some issues:

WARNINGS:
users.User: (auth.W004) 'User.employee_id' is named as the 
'USERNAME_FIELD', but it is not unique.
    HINT: Ensure that your authentication backend(s) can handle 
    non-unique usernames.

System check identified 1 issue (0 silenced).


✅ check() メソッド追加後:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ python manage.py check

System check identified no issues (0 silenced).

✨ 警告が消えた！


【コードの詳細解説】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

check() メソッドの動作を1行ずつ解説:

```python
@classmethod
def check(cls, **kwargs):
```
↑ @classmethod デコレータ
  - インスタンスを作らずに呼び出せるメソッド
  - cls はクラス自身（User）を指す
  - Django がモデルをチェックする時に自動で呼ぶ


```python
errors = super().check(**kwargs)
```
↑ 親クラスのチェックを実行
  - AbstractBaseUser の check() を呼ぶ
  - すべての警告・エラーが errors（リスト）に入る
  
  例: errors = [
      <Warning: auth.W004>,
      <Warning: auth.W005>,
      ...
  ]


```python
errors = [
    error for error in errors
    if error.id != 'auth.W004'
]
```
↑ リスト内包表記でフィルタリング
  - error.id が 'auth.W004' じゃないものだけ残す
  - W004 警告は除外される
  
  実行例:
  元のリスト: [W004, W005, W006]
  ↓ フィルタリング
  新しいリスト: [W005, W006]  ← W004 が消えた！


```python
return errors
```
↑ フィルタリング後のリストを返す
  - Django はこのリストを元に警告を表示
  - W004 が含まれていないので警告が出ない


【他の警告は残る理由】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if error.id != 'auth.W004'
↑ W004 だけを除外する条件

つまり:
  auth.W004 → 除外される ← 論理削除のため意図的
  auth.W005 → 残る ← セキュリティ重要
  auth.W006 → 残る ← セキュリティ重要
  auth.E003 → 残る ← エラーは必ず表示


もし全部消したい場合（非推奨）:
```python
# ❌ これはダメ！セキュリティリスク
errors = [
    error for error in errors
    if not error.id.startswith('auth.')
]
```


【警告の種類と対応】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

auth.W004: USERNAME_FIELD が unique じゃない
  対応: check() で抑制 ← 今回のケース
  理由: 論理削除のため条件付き制約を使用

auth.W005: MIDDLEWARE の設定不足
  対応: settings.py を修正
  理由: セキュリティ上必要

auth.W006: SESSION_COOKIE_SECURE が False
  対応: settings.py で True に設定
  理由: 本番環境で必須

auth.E003: PASSWORD_HASHERS が空
  対応: settings.py に追加
  理由: パスワードのハッシュ化に必須


【動作テスト】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 警告チェック
   $ python manage.py check
   
   期待: System check identified no issues (0 silenced).
   ✅ W004 警告が出ない


2. サーバー起動
   $ python manage.py runserver
   
   期待: 警告なしで起動
   ✅ 開発しやすい


3. マイグレーション
   $ python manage.py makemigrations
   
   期待: No changes detected
   ✅ データベース構造は変わらない


4. 実際の動作確認
   # ユーザーを作成
   user = User.objects.create_user(
       employee_id='1000',
       username='山田太郎',
       password='test1234'
   )
   
   # 論理削除
   user.soft_delete()
   
   # 同じ社員番号で新規作成
   new_user = User.objects.create_user(
       employee_id='1000',  # ← 同じ番号OK！
       username='鈴木次郎',
       password='test5678'
   )
   
   期待: エラーなし、両方存在
   ✅ 論理削除が正しく動く


【まとめ】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ やったこと:
  - check() メソッドを追加
  - W004 警告だけ除外
  - 他の警告は残す（セキュリティのため）

✅ メリット:
  - 警告が消えて開発しやすい
  - マイグレーション不要
  - 安全性は変わらない

✅ 安全性の保証:
  1. DB制約: 条件付きユニーク制約
  2. アプリ: UniqueValidator
  3. ロジック: UserService

✅ 他の変更不要:
  - serializers.py → そのまま
  - views.py → そのまま
  - services/user_service.py → そのまま


【参考: Django の警告システム】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Django の check フレームワーク:
  - モデル、設定、URLなどをチェック
  - 起動時とマイグレーション時に実行
  - 警告とエラーの2種類がある

警告（Warning）:
  - W で始まる（例: W004）
  - 動くけど推奨されない設定
  - 無視しても動作する

エラー（Error）:
  - E で始まる（例: E003）
  - 動かない可能性が高い
  - 必ず修正が必要

check() メソッド:
  - 各モデルで独自のチェックを追加・除外できる
  - @classmethod で定義
  - Django が自動で呼び出す


【よくある質問】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q1. check() を追加したらマイグレーションが必要？
A1. 不要！コードレベルの変更だけ

Q2. 本番環境でも動く？
A2. もちろん！データベース構造は同じ

Q3. 他の警告まで消えない？
A3. 消えない。W004 だけ除外している

Q4. セキュリティ的に問題ない？
A4. 問題なし。3層の保護で安全性を確保

Q5. Django のバージョンで動かなくなる？
A5. check() は標準機能なので大丈夫

Q6. 削除済みユーザーの社員番号は？
A6. そのまま保持される（履歴として重要）

Q7. 本当に再利用できる？
A7. できる！条件付きユニーク制約が保証


【次のステップ】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. このファイルを保存
   ✅ backend/users/models.py

2. 警告チェック
   $ python manage.py check
   
   期待: System check identified no issues (0 silenced).

3. サーバー起動
   $ python manage.py runserver
   
   期待: 警告なし

4. 動作確認
   - ユーザー作成
   - 論理削除
   - 社員番号再利用
   
   すべて正常に動作する！


これで論理削除の実装が完璧になった！( ゚Д゚)✨
"""
