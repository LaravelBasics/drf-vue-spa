from django.contrib import admin

# Register your models here.
# backend/audit/admin.py
from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'request_id', 'employee_id', 'action', 'model_name', 'object_id', 'success']
    list_filter = ['action', 'model_name', 'success', 'timestamp']
    search_fields = ['request_id', 'employee_id', 'username', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'