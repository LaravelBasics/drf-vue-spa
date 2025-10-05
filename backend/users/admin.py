# backend/users/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    """カスタムユーザー管理画面"""
    
    # リスト表示
    list_display = [
        'employee_id',
        'username', 
        'email',
        'is_admin', 
        'is_active',
        'is_deleted',
        'created_at'
    ]
    
    list_filter = [
        'is_admin', 
        'is_active',
        'is_staff',
        'created_at',
        'deleted_at',
    ]
    
    # 検索フィールド
    search_fields = ['employee_id', 'username', 'email']
    
    # 並び順
    ordering = ['-created_at']
    
    # 詳細画面のフィールド設定
    fieldsets = (
        ('認証情報', {
            'fields': ('employee_id', 'password')
        }),
        ('個人情報', {
            'fields': ('username', 'email')
        }),
        ('権限', {
            'fields': (
                'is_active',
                'is_admin',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('タイムスタンプ', {
            'fields': ('created_at', 'updated_at', 'deleted_at', 'last_login'),
            'classes': ('collapse',),
        }),
    )
    
    # 新規作成時のフィールド
    add_fieldsets = (
        ('認証情報（必須）', {
            'classes': ('wide',),
            'fields': ('employee_id', 'password1', 'password2'),
        }),
        ('個人情報（任意）', {
            'fields': ('username', 'email'),
        }),
        ('権限', {
            'fields': ('is_active', 'is_admin', 'is_staff', 'is_superuser'),
        }),
    )
    
    # 読み取り専用フィールド
    readonly_fields = ['created_at', 'updated_at', 'deleted_at', 'last_login']
    
    # 削除済み判定
    @admin.display(boolean=True, description='削除済み')
    def is_deleted(self, obj):
        return obj.deleted_at is not None
    
    # アクション
    actions = ['restore_users', 'soft_delete_users']
    
    @admin.action(description='選択したユーザーを復元')
    def restore_users(self, request, queryset):
        count = 0
        for user in queryset:
            if user.deleted_at:
                user.restore()
                count += 1
        self.message_user(request, f'{count}人のユーザーを復元しました。')
    
    @admin.action(description='選択したユーザーを論理削除')
    def soft_delete_users(self, request, queryset):
        count = 0
        for user in queryset:
            if not user.deleted_at:
                user.soft_delete()
                count += 1
        self.message_user(request, f'{count}人のユーザーを論理削除しました。')
    
    def get_queryset(self, request):
        """削除済みユーザーも表示"""
        return User.all_objects.all()
    
    def get_form(self, request, obj=None, **kwargs):
        """新規作成時と編集時でフィールドセットを切り替え"""
        if obj is None:
            self.fieldsets = self.add_fieldsets
        else:
            self.fieldsets = (
                ('認証情報', {'fields': ('employee_id', 'password')}),
                ('個人情報', {'fields': ('username', 'email')}),
                ('権限', {
                    'fields': (
                        'is_active', 'is_admin', 'is_staff', 'is_superuser',
                        'groups', 'user_permissions',
                    )
                }),
                ('タイムスタンプ', {
                    'fields': ('created_at', 'updated_at', 'deleted_at', 'last_login'),
                    'classes': ('collapse',),
                }),
            )
        return super().get_form(request, obj, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """パスワードのハッシュ化処理"""
        if not change:  # 新規作成時
            obj.set_password(form.cleaned_data['password1'])
        elif 'password' in form.changed_data:  # パスワード変更時
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)