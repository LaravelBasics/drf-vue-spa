# 1. backend/audit/models.py
# ============================================
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class AuditLog(models.Model):
    """監査ログモデル"""
    
    ACTION_CHOICES = [
        ('CREATE', '作成'),
        ('UPDATE', '更新'),
        ('DELETE', '削除'),
        ('LOGIN', 'ログイン'),
        ('LOGOUT', 'ログアウト'),
        ('LOGIN_FAILED', 'ログイン失敗'),
        ('VIEW', '閲覧'),
        ('RESTORE', '復元'),
        ('BULK_DELETE', '一括削除'),
        ('BULK_RESTORE', '一括復元'),
    ]
    
    # リクエスト識別情報
    request_id = models.CharField(
        'リクエストID',
        max_length=36,
        db_index=True,
        help_text='X-Request-ID または自動生成されたUUID'
    )
    
    # ユーザー情報
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='実行ユーザー',
        related_name='audit_logs'
    )
    
    employee_id = models.CharField(
        '社員番号',
        max_length=20,
        null=True,
        blank=True,
        help_text='削除されたユーザーのために保存'
    )
    
    username = models.CharField(
        'ユーザー名',
        max_length=50,
        null=True,
        blank=True
    )
    
    # アクション情報
    action = models.CharField(
        'アクション',
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True
    )
    
    model_name = models.CharField(
        'モデル名',
        max_length=50,
        db_index=True,
        help_text='User, Product など'
    )
    
    object_id = models.CharField(
        'オブジェクトID',
        max_length=50,
        null=True,
        blank=True
    )
    
    # 変更内容
    changes = models.JSONField(
        '変更内容',
        null=True,
        blank=True,
        help_text='変更前後の値を記録'
    )
    
    # リクエスト情報
    ip_address = models.GenericIPAddressField(
        'IPアドレス',
        null=True,
        blank=True
    )
    
    user_agent = models.TextField(
        'User Agent',
        null=True,
        blank=True
    )
    
    endpoint = models.CharField(
        'エンドポイント',
        max_length=255,
        null=True,
        blank=True,
        help_text='/api/users/1/ など'
    )
    
    method = models.CharField(
        'HTTPメソッド',
        max_length=10,
        null=True,
        blank=True,
        help_text='GET, POST, PUT, DELETE など'
    )
    
    # メタ情報
    success = models.BooleanField(
        '成功',
        default=True
    )
    
    error_message = models.TextField(
        'エラーメッセージ',
        null=True,
        blank=True
    )
    
    timestamp = models.DateTimeField(
        '実行日時',
        default=timezone.now,
        db_index=True
    )
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = '監査ログ'
        verbose_name_plural = '監査ログ'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['request_id']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['model_name', 'object_id']),
        ]
    
    def __str__(self):
        user_str = self.employee_id or 'Anonymous'
        return f"{user_str} - {self.action} - {self.model_name} - {self.timestamp}"