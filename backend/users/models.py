from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.utils import timezone


class SoftDeleteManager(BaseUserManager):
    """論理削除に対応したマネージャー"""
    
    def get_queryset(self):
        """削除済みを除外したクエリセットを返す"""
        return super().get_queryset().filter(deleted_at__isnull=True)
    
    def with_deleted(self):
        """削除済みを含むクエリセットを返す"""
        return super().get_queryset()
    
    def deleted_only(self):
        """削除済みのみのクエリセットを返す"""
        return super().get_queryset().filter(deleted_at__isnull=False)

    # 🚨 必須の create_user メソッドを SoftDeleteManager に追加 🚨
    def create_user(self, username, employee_id=None, password=None, **extra_fields):
        if not username:
            raise ValueError('ユーザー名を設定する必要があります')
        
        # self.normalize_username を、モデルのクラスメソッドとして呼び出すように変更
        username = self.model.normalize_username(username)

        user = self.model(
            username=username,
            employee_id=employee_id,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, employee_id, password=None, **extra_fields):
        # BaseUserManagerの慣習に従い、employee_idを引数に追加
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_admin', True) # あなたのカスタムフィールド
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(username, employee_id, password, **extra_fields)

class CustomUser(AbstractUser):
    """カスタムユーザーモデル（論理削除対応）"""
    
    employee_id = models.PositiveIntegerField(
        unique=True,
        verbose_name="社員番号",
        help_text="10桁以内の数字",
    )
    
    is_admin = models.BooleanField(
        default=False,
        verbose_name="管理者権限"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="登録日時"
    )
    
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="削除日時",
        db_index=True  # 検索高速化のためインデックス追加
    )
    
    username = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="ユーザー名"
    )

    # デフォルトマネージャー（削除済み除外）
    objects = SoftDeleteManager()
    
    # すべてのオブジェクトを扱うマネージャー
    all_objects = models.Manager()

    class Meta:
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー一覧"
        ordering = ['-created_at']
        db_table = 'custom_user'
        indexes = [
            models.Index(fields=['deleted_at', 'is_active']),  # 複合インデックス
            models.Index(fields=['deleted_at', 'is_admin']),
        ]

    def clean(self):
        super().clean()
        if self.employee_id and len(str(self.employee_id)) > 10:
            raise ValidationError({
                'employee_id': '社員番号は10桁以内で入力してください。'
            })
    
    def soft_delete(self):
        """論理削除"""
        self.deleted_at = timezone.now()
        self.is_active = False  # 同時に無効化
        self.save(update_fields=['deleted_at', 'is_active'])
    
    def restore(self):
        """復元"""
        self.deleted_at = None
        self.is_active = True
        self.save(update_fields=['deleted_at', 'is_active'])
    
    def hard_delete(self):
        """物理削除（管理者用）"""
        super().delete()
    
    @property
    def is_deleted(self):
        """削除済みかどうか"""
        return self.deleted_at is not None
    
    def __str__(self):
        status = " [削除済み]" if self.is_deleted else ""
        if self.employee_id:
            return f"{self.username} ({self.employee_id}){status}"
        return f"{self.username}{status}"