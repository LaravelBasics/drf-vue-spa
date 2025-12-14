# common/models.py
from django.db import models
from django.contrib.auth.hashers import check_password, make_password


class MGroup(models.Model):
    group_id = models.CharField(primary_key=True, max_length=50)
    group_name = models.CharField(max_length=100)
    is_active = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "m_group"

    def __str__(self):
        return f"{self.group_id} - {self.group_name}"


class MGroupPermissions(models.Model):
    pk = models.CompositePrimaryKey("group_id", "permission_code")
    group_id = models.CharField(max_length=50)
    permission_code = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "m_group_permissions"
        unique_together = (("group_id", "permission_code"),)


class MUser(models.Model):
    """
    レガシーシステム対応カスタムユーザーモデル

    PostgreSQLテーブル構造:
    - is_superuser: 管理者権限フラグ（Boolean）
    - is_staff: 管理画面アクセス権フラグ（Boolean）
    - is_admin カラムは存在しない（後方互換性のためプロパティで提供）
    """

    user_id = models.CharField(primary_key=True, max_length=50)
    password = models.CharField(max_length=128)
    username = models.CharField(max_length=50)
    last_login = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)

    # ✅ PostgreSQLに存在するフィールド
    is_superuser = models.BooleanField(blank=True, null=True)  # 管理者権限
    is_staff = models.BooleanField(blank=True, null=True)  # 管理画面アクセス権

    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "m_user"

    # ========================================
    # Django認証システム必須設定
    # ========================================

    USERNAME_FIELD = "user_id"
    REQUIRED_FIELDS = []

    # ========================================
    # 認証プロパティ（必須）
    # ========================================

    @property
    def is_authenticated(self):
        """常にTrue（ログイン済みユーザー）"""
        return True

    @property
    def is_anonymous(self):
        """常にFalse（匿名ユーザーではない）"""
        return False

    @property
    def is_admin(self):
        """
        管理者権限チェック（後方互換性のためのプロパティ）

        is_superuser=True または is_staff=True なら管理者とみなす

        Returns:
            bool: 管理者ならTrue
        """
        return bool(self.is_superuser or self.is_staff)

    # ========================================
    # パスワード管理
    # ========================================

    def check_password(self, raw_password):
        """
        パスワード検証

        対応ハッシュ形式（Django標準）:
        - PBKDF2-SHA256: pbkdf2_sha256$600000$xxxxx$yyyyy
        - PBKDF2-SHA1: pbkdf2_sha1$xxxxx$yyyyy (レガシー互換用)
        """
        return check_password(raw_password, self.password)

    def set_password(self, raw_password):
        """
        パスワードをハッシュ化して設定

        settings.pyのPASSWORD_HASHERSの最初のアルゴリズムを使用
        デフォルトはPBKDF2-SHA256（Django標準、追加パッケージ不要）
        """
        self.password = make_password(raw_password)

    # ========================================
    # 権限管理（is_superuser または is_staff ベース）
    # ========================================

    def has_perm(self, perm, obj=None):
        """
        特定の権限を持っているか

        is_superuser=True または is_staff=True なら全ての権限を持つ
        """
        return self.is_active and (self.is_superuser or self.is_staff)

    def has_perms(self, perm_list, obj=None):
        """
        複数の権限を持っているか

        is_superuser=True または is_staff=True なら全ての権限を持つ
        """
        return self.is_active and (self.is_superuser or self.is_staff)

    def has_module_perms(self, app_label):
        """
        特定のアプリへのアクセス権限

        is_superuser=True または is_staff=True なら全てのアプリにアクセス可能
        """
        return self.is_active and (self.is_superuser or self.is_staff)

    # ========================================
    # セッション管理
    # ========================================

    def get_session_auth_hash(self):
        """セッションハッシュ（パスワード変更時のセッション無効化用）"""
        from django.utils.crypto import salted_hmac

        key_salt = "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash"
        return salted_hmac(key_salt, self.password).hexdigest()

    # ========================================
    # ユーティリティ
    # ========================================

    def __str__(self):
        return self.user_id

    def get_username(self):
        """USERNAME_FIELDの値を返す"""
        return self.user_id


class MUserGroup(models.Model):
    pk = models.CompositePrimaryKey("user_id", "group_id")
    user_id = models.CharField(max_length=50)
    group_id = models.CharField(max_length=50)
    is_active = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "m_user_group"
        unique_together = (("user_id", "group_id"),)


# ========================================
# レガシーシステム運用メモ
# ========================================
"""
【PostgreSQLテーブル構造】

m_user テーブル:
- user_id (VARCHAR(50), PRIMARY KEY)
- password (VARCHAR(128))
- username (VARCHAR(50))
- last_login (TIMESTAMP)
- is_active (BOOLEAN)
- is_superuser (BOOLEAN) ← 管理者権限
- is_staff (BOOLEAN)     ← 管理画面アクセス権
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

【管理者権限の設定】

-- ユーザーを管理者に設定
UPDATE legacy_schema.m_user 
SET is_superuser = TRUE, is_staff = TRUE 
WHERE user_id = 'admin001';

-- スーパーユーザーのみ
UPDATE legacy_schema.m_user 
SET is_superuser = TRUE, is_staff = FALSE 
WHERE user_id = 'user001';

-- 管理画面アクセスのみ
UPDATE legacy_schema.m_user 
SET is_superuser = FALSE, is_staff = TRUE 
WHERE user_id = 'staff001';

【Pythonでの管理者判定】

from common.models import MUser

user = MUser.objects.get(user_id='admin001')

# ✅ is_adminプロパティを使用（推奨）
if user.is_admin:
    print('管理者です')

# ✅ 直接フィールドを確認
if user.is_superuser or user.is_staff:
    print('管理者です')

【パスワードハッシュ化】

from django.contrib.auth.hashers import make_password
from common.models import MUser

# 新規ユーザー作成
hashed = make_password('password123')
user = MUser(
    user_id='test001',
    password=hashed,
    username='テストユーザー',
    is_active=True,
    is_superuser=False,
    is_staff=False
)
user.save()

# 既存ユーザーのパスワード変更
user = MUser.objects.get(user_id='test001')
user.set_password('newpassword456')
user.save()
"""
