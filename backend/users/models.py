from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone

class CustomUser(AbstractUser):
    """カスタムユーザーモデル"""
    
    employee_id = models.PositiveIntegerField(
        unique=True,
        verbose_name="社員番号",
        help_text="10桁以内の数字",
        # null=True,  # 既存のスーパーユーザー対応
        # blank=True,
    )
    
    is_admin = models.BooleanField(
        default=False,
        verbose_name="管理者権限"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,  # 自動で作成日時を設定
        verbose_name="登録日時"
    )
    
    username = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="ユーザー名"
    )

    class Meta:
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー一覧"
        ordering = ['-created_at']
        db_table = 'custom_user'  # テーブル名を明示

    def clean(self):
        super().clean()
        if self.employee_id and len(str(self.employee_id)) > 10:
            raise ValidationError({
                'employee_id': '社員番号は10桁以内で入力してください。'
            })
    
    def __str__(self):
        if self.employee_id:
            return f"{self.username} ({self.employee_id})"
        return self.username