"""
カスタムユーザーモデル

Features:
- employee_id でログイン
- 論理削除対応（deleted_at）
- 条件付きユニーク制約で番号再利用可能
"""

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """論理削除対応マネージャー（削除済み除外）"""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def create_user(self, employee_id, password=None, **extra_fields):
        """通常ユーザー作成"""
        if not employee_id:
            raise ValueError("社員番号は必須です")

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_admin", False)

        user = self.model(employee_id=employee_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, employee_id, password=None, **extra_fields):
        """スーパーユーザー作成"""
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_admin") is not True:
            raise ValueError("スーパーユーザーは is_admin=True である必要があります")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("スーパーユーザーは is_staff=True である必要があります")

        return self.create_user(employee_id, password, **extra_fields)


class AllObjectsManager(BaseUserManager):
    """全レコード取得マネージャー（削除済み含む）"""

    def get_queryset(self):
        return super().get_queryset()


class User(AbstractBaseUser, PermissionsMixin):
    """
    カスタムユーザーモデル

    論理削除:
    - employee_id はそのまま保持
    - deleted_at が NULL = アクティブ、値あり = 削除済み
    - 条件付きユニーク制約で番号再利用可能
    """

    # 認証フィールド
    employee_id = models.CharField(
        "社員番号",
        max_length=50,
        unique=False,  # 条件付きユニーク制約を使用
        db_index=True,
    )

    # 個人情報
    username = models.CharField("ユーザー名", max_length=50, blank=True, null=True)
    email = models.EmailField("メールアドレス", max_length=255, blank=True, null=True)

    # 権限
    is_admin = models.BooleanField("管理者", default=False)
    is_staff = models.BooleanField("スタッフ", default=False)
    is_active = models.BooleanField("アクティブ", default=True)

    # タイムスタンプ
    created_at = models.DateTimeField("作成日時", default=timezone.now)
    updated_at = models.DateTimeField("更新日時", auto_now=True)
    deleted_at = models.DateTimeField("削除日時", blank=True, null=True)

    # Django認証設定
    USERNAME_FIELD = "employee_id"
    REQUIRED_FIELDS = ["username"]

    # マネージャー
    objects = CustomUserManager()
    all_objects = AllObjectsManager()

    class Meta:
        db_table = "users"
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー"
        ordering = ["-created_at"]

        # 条件付きユニーク制約（論理削除対応）
        constraints = [
            models.UniqueConstraint(
                fields=["employee_id"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_active_employee_id",
            )
        ]

        indexes = [
            models.Index(fields=["employee_id"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["deleted_at"]),
            models.Index(fields=["is_admin", "is_active"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        status = " [削除済み]" if self.deleted_at else ""
        return f"{self.employee_id} ({self.username or '名前未設定'}){status}"

    def soft_delete(self):
        """論理削除"""
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()

    def restore(self):
        """復元"""
        self.deleted_at = None
        self.is_active = True
        self.save()

    @property
    def display_name(self):
        """表示名"""
        return self.username or self.employee_id

    def has_perm(self, perm, obj=None):
        """権限チェック"""
        return self.is_admin or super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        """アプリ権限チェック"""
        return self.is_admin or super().has_module_perms(app_label)
