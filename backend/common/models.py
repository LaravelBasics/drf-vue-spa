from django.db import models
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractBaseUser


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
    user_id = models.CharField(primary_key=True, max_length=50)
    password = models.CharField(max_length=128)
    username = models.CharField(max_length=50)
    last_login = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    is_superuser = models.BooleanField(blank=True, null=True)
    is_staff = models.BooleanField(blank=True, null=True)
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
    def is_staff(self):
        """Django管理画面アクセス権限（is_adminと連動）"""
        return self.is_admin

    @property
    def is_superuser(self):
        """スーパーユーザー権限（is_adminと連動）"""
        return self.is_admin

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
    # 権限管理（is_adminベース）
    # ========================================

    def has_perm(self, perm, obj=None):
        """特定の権限を持っているか"""
        return self.is_active and self.is_admin

    def has_perms(self, perm_list, obj=None):
        """複数の権限を持っているか"""
        return self.is_active and self.is_admin

    def has_module_perms(self, app_label):
        """特定のアプリへのアクセス権限"""
        return self.is_active and self.is_admin

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
    # リレーション代替（手動JOIN）
    # ========================================

    # @property
    # def user(self):
    #     """遅延評価でUserを取得"""
    #     try:
    #         return MUser.objects.get(user_id=self.user_id)
    #     except MUser.DoesNotExist:
    #         return None

    # @property
    # def group(self):
    #     """遅延評価でGroupを取得"""
    #     try:
    #         return MGroup.objects.get(group_id=self.group_id)
    #     except MGroup.DoesNotExist:
    #         return None

    # def __str__(self):
    #     return f"{self.user_id} - {self.group_id}"


# QuerySetヘルパー（User.groups_rel）
# ========================================

# Userモデルに逆参照用のプロパティを追加
# MUser.groups_rel = property(
#     lambda self: MUserGroup.objects.filter(user_id=self.user_id)
# )
