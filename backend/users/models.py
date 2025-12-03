"""
グループ認証対応のユーザーモデル

Features:
- user_id がプライマリキー（ナチュラルキー）
- グループとの多対多リレーション
- 論理削除なし（is_activeのみで管理）
"""

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """カスタムユーザーマネージャー"""

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


class Group(models.Model):
    """ユーザーグループ"""

    group_id = models.CharField("グループID", max_length=50, primary_key=True)
    group_name = models.CharField("グループ名", max_length=100, db_column="group_name")
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

    # 認証フィールド
    user_id = models.CharField(
        "ユーザーID",
        max_length=50,
        primary_key=True,
        db_column="user_id",
    )

    # 個人情報
    username = models.CharField(
        "ユーザー名",
        max_length=50,
        blank=True,
        null=True,
        db_column="username",
    )
    email = models.EmailField(
        "メールアドレス",
        max_length=255,
        blank=True,
        null=True,
        db_column="email",
    )

    # グループリレーション
    groups_rel = models.ManyToManyField(
        Group,
        through="UserGroup",
        related_name="users",
        verbose_name="所属グループ",
    )

    # 権限
    is_admin = models.BooleanField("管理者", default=False, db_column="is_admin")
    is_active = models.BooleanField("アクティブ", default=True, db_column="is_active")

    # タイムスタンプ
    created_at = models.DateTimeField("作成日時", default=timezone.now)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    # Django認証設定
    USERNAME_FIELD = "user_id"
    REQUIRED_FIELDS = ["username"]

    # マネージャー
    objects = CustomUserManager()

    class Meta:
        db_table = "users"
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user_id} ({self.username or '名前未設定'})"


class UserGroup(models.Model):
    """
    ユーザーとグループの中間テーブル

    複合キー: (user_id, group_id)
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="ユーザー",
        db_column="user_id",
        related_name="user_groups",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        verbose_name="グループ",
        db_column="group_id",
        related_name="group_users",
    )
    is_active = models.BooleanField(
        "アクティブ",
        default=True,
        db_column="is_active",
        help_text="グループへの所属が有効かどうか",
    )
    joined_at = models.DateTimeField("参加日時", default=timezone.now)

    class Meta:
        db_table = "user_groups"
        verbose_name = "ユーザーグループ"
        verbose_name_plural = "ユーザーグループ"
        unique_together = ("user", "group")

    def __str__(self):
        return f"{self.user.user_id} @ {self.group.group_name}"
