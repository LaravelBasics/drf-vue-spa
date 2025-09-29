from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """カスタムユーザー管理画面"""
    
    list_display = [
        'username', 'employee_id', 'is_admin', 
        'is_active', 'created_at'
    ]
    
    list_filter = [
        'is_admin', 'is_active', 'created_at'
    ]
    
    search_fields = ['username', 'employee_id']
    
    fieldsets = UserAdmin.fieldsets + (
        ('カスタムフィールド', {
            'fields': ('employee_id', 'is_admin', 'created_at')
        }),
    )
    
    readonly_fields = ['created_at']
    
    ordering = ['-created_at']
