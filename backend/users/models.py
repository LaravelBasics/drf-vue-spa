# backend/users/models.py
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """カスタムユーザーマネージャー"""
    
    def create_user(self, employee_id, password=None, **extra_fields):
        """通常のユーザーを作成"""
        if not employee_id:
            raise ValueError('社員番号は必須です')
        
        # デフォルト値を設定
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_admin', False)
        
        user = self.model(employee_id=employee_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, employee_id, password=None, **extra_fields):
        """スーパーユーザーを作成"""
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_admin') is not True:
            raise ValueError('スーパーユーザーは is_admin=True である必要があります')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('スーパーユーザーは is_staff=True である必要があります')
        
        return self.create_user(employee_id, password, **extra_fields)


class SoftDeleteManager(models.Manager):
    """論理削除対応マネージャー（削除済みを除外）"""
    
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class User(AbstractBaseUser, PermissionsMixin):
    """
    カスタムユーザーモデル
    
    特徴:
    - employee_id（社員番号）で認証
    - username（ユーザー名）はユニーク制約なしの表示名
    - 論理削除対応
    - email は任意（必要に応じて unique 制約を追加可能）
    """
    
    # ==================== 認証フィールド ====================
    employee_id = models.CharField(
        '社員番号',
        max_length=20,
        unique=True,
        db_index=True,
        help_text='ログイン認証に使用する一意の社員番号'
    )
    
    # ==================== 表示名・個人情報 ====================
    username = models.CharField(
        'ユーザー名',
        max_length=50,
        blank=True,
        null=True,
        help_text='表示用のユーザー名（ユニーク制約なし）'
    )
    
    email = models.EmailField(
        'メールアドレス',
        max_length=255,
        blank=True,
        null=True,
        # 必要に応じて unique=True に変更可能
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
        help_text='Django管理サイトにアクセスできるかどうか'
    )
    
    is_active = models.BooleanField(
        'アクティブ',
        default=True,
        help_text='アカウントが有効かどうか'
    )
    
    # ==================== タイムスタンプ ====================
    created_at = models.DateTimeField(
        '作成日時',
        default=timezone.now
    )
    
    updated_at = models.DateTimeField(
        '更新日時',
        auto_now=True
    )
    
    # 論理削除用
    deleted_at = models.DateTimeField(
        '削除日時',
        blank=True,
        null=True
    )
    
    # ==================== Django認証設定 ====================
    # 認証に使うフィールドを employee_id に設定
    USERNAME_FIELD = 'employee_id'
    
    # createsuperuser コマンドで追加入力を求めるフィールド
    # (employee_id と password は自動的に聞かれるので不要)
    REQUIRED_FIELDS = ['username']
    
    # ==================== マネージャー ====================
    objects = SoftDeleteManager()  # デフォルトは削除済み除外
    all_objects = models.Manager()  # すべてのレコードにアクセス
    
    class Meta:
        db_table = 'users'
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['is_active']),
            models.Index(fields=['deleted_at']),
        ]
    
    def __str__(self):
        return f"{self.employee_id} ({self.username or '名前未設定'})"
    
    # ==================== カスタムメソッド ====================
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
        """表示用の名前を取得"""
        return self.username or self.employee_id
    
    def has_perm(self, perm, obj=None):
        """権限チェック（管理者は常にTrue）"""
        return self.is_admin or super().has_perm(perm, obj)
    
    def has_module_perms(self, app_label):
        """アプリケーションの権限チェック"""
        return self.is_admin or super().has_module_perms(app_label)