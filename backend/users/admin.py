"""
Django管理画面カスタマイズ
"""

from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    """ユーザー管理画面"""

    list_display = [
        "employee_id",
        "username",
        "email",
        "is_admin",
        "is_active",
        "is_deleted",
        "created_at",
    ]

    list_filter = ["is_admin", "is_active", "is_staff", "created_at", "deleted_at"]
    search_fields = ["employee_id", "username", "email"]
    ordering = ["-created_at"]

    fieldsets = (
        ("認証情報", {"fields": ("employee_id", "password")}),
        ("個人情報", {"fields": ("username", "email")}),
        (
            "権限",
            {
                "fields": (
                    "is_active",
                    "is_admin",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "タイムスタンプ",
            {
                "fields": ("created_at", "updated_at", "deleted_at", "last_login"),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets = (
        (
            "認証情報",
            {
                "classes": ("wide",),
                "fields": ("employee_id", "password1", "password2"),
            },
        ),
        (
            "個人情報",
            {
                "fields": ("username", "email"),
            },
        ),
        (
            "権限",
            {
                "fields": ("is_active", "is_admin", "is_staff", "is_superuser"),
            },
        ),
    )

    readonly_fields = ["created_at", "updated_at", "deleted_at", "last_login"]
    actions = ["restore_users", "soft_delete_users"]

    @admin.display(boolean=True, description="削除済み")
    def is_deleted(self, obj):
        return obj.deleted_at is not None

    @admin.action(description="選択したユーザーを復元")
    def restore_users(self, request, queryset):
        count = 0
        for user in queryset.filter(deleted_at__isnull=False):
            user.restore()
            count += 1
        self.message_user(request, f"{count}人のユーザーを復元しました")

    @admin.action(description="選択したユーザーを論理削除")
    def soft_delete_users(self, request, queryset):
        count = 0
        for user in queryset.filter(deleted_at__isnull=True):
            user.soft_delete()
            count += 1
        self.message_user(request, f"{count}人のユーザーを論理削除しました")

    def get_queryset(self, request):
        """削除済みも含めて表示"""
        return User.all_objects.all()

    def save_model(self, request, obj, form, change):
        """パスワードをハッシュ化して保存"""
        if not change:
            # 新規作成時
            if "password1" in form.cleaned_data:
                obj.set_password(form.cleaned_data["password1"])
        elif change and "password" in form.cleaned_data:
            # 更新時（パスワードが入力されている場合のみ）
            password = form.cleaned_data["password"]
            if password:
                obj.set_password(password)

        super().save_model(request, obj, form, change)
