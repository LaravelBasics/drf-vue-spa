"""
グループ認証対応のユーザーモデル

Features:
- user_id がプライマリキー（employee_idから変更）
- グループとの多対多リレーション
- 論理削除対応
"""

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """論理削除対応マネージャー"""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def create_user(self, user_id, password=None, **extra_fields):
        """通常ユーザー作成"""
        if not user_id:
            raise ValueError("ユーザーIDは必須です")

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_admin", False)

        user = self.model(user_id=user_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class AllObjectsManager(BaseUserManager):
    """全レコード取得マネージャー"""

    def get_queryset(self):
        return super().get_queryset()


class Group(models.Model):
    """ユーザーグループ"""

    group_id = models.CharField("グループID", max_length=50, primary_key=True)
    group_name = models.CharField("グループ名", max_length=100)
    is_active = models.BooleanField("アクティブ", default=True)
    created_at = models.DateTimeField("作成日時", default=timezone.now)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        db_table = "groups"
        verbose_name = "グループ"
        verbose_name_plural = "グループ"
        ordering = ["group_id"]

    def __str__(self):
        return f"{self.group_name} ({self.group_id})"


class User(AbstractBaseUser, PermissionsMixin):
    """
    グループ認証対応ユーザーモデル

    認証方法:
    - グループID + ユーザーID + パスワード の3点セット
    """

    # 認証フィールド（employee_id → user_id に変更）
    user_id = models.CharField(
        "ユーザーID",
        max_length=50,
        primary_key=True,  # プライマリキー
    )

    # 個人情報
    username = models.CharField("ユーザー名", max_length=50, blank=True, null=True)
    email = models.EmailField("メールアドレス", max_length=255, blank=True, null=True)

    # グループリレーション
    groups_rel = models.ManyToManyField(
        Group,
        through="UserGroup",
        related_name="users",
        verbose_name="所属グループ",
    )

    # 権限
    is_admin = models.BooleanField("管理者", default=False)
    is_staff = models.BooleanField("スタッフ", default=False)
    is_active = models.BooleanField("アクティブ", default=True)

    # タイムスタンプ
    created_at = models.DateTimeField("作成日時", default=timezone.now)
    updated_at = models.DateTimeField("更新日時", auto_now=True)
    deleted_at = models.DateTimeField("削除日時", blank=True, null=True)

    # Django認証設定
    USERNAME_FIELD = "user_id"
    REQUIRED_FIELDS = ["username"]

    # マネージャー
    objects = CustomUserManager()
    all_objects = AllObjectsManager()

    class Meta:
        db_table = "users"
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー"
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["deleted_at"]),
            models.Index(fields=["is_admin", "is_active"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        status = " [削除済み]" if self.deleted_at else ""
        return f"{self.user_id} ({self.username or '名前未設定'}){status}"

    def soft_delete(self):
        """論理削除"""
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["deleted_at", "is_active"])

    def restore(self):
        """復元"""
        self.deleted_at = None
        self.is_active = True
        self.save(update_fields=["deleted_at", "is_active"])

    @property
    def display_name(self):
        """表示名"""
        return self.username or self.user_id

    def has_perm(self, perm, obj=None):
        """権限チェック"""
        return self.is_admin or super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        """アプリ権限チェック"""
        return self.is_admin or super().has_module_perms(app_label)


class UserGroup(models.Model):
    """
    ユーザーとグループの中間テーブル

    複合キー: (user_id, group_id)
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="ユーザー", db_column="user_id"
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, verbose_name="グループ", db_column="group_id"
    )
    joined_at = models.DateTimeField("参加日時", default=timezone.now)

    class Meta:
        db_table = "user_groups"
        verbose_name = "ユーザーグループ"
        verbose_name_plural = "ユーザーグループ"
        unique_together = ("user", "group")  # 複合ユニークキー
        indexes = [
            models.Index(fields=["user", "group"]),
            models.Index(fields=["group"]),
        ]

    def __str__(self):
        return f"{self.user.user_id} @ {self.group.group_name}"
