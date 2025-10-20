"""
Django管理画面カスタマイズ
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms

User = get_user_model()


class UserCreationForm(forms.ModelForm):
    """管理画面でのユーザー作成フォーム"""

    password1 = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput,
        help_text="8文字以上で入力してください",
    )
    password2 = forms.CharField(
        label="パスワード（確認）",
        widget=forms.PasswordInput,
        help_text="確認のため、もう一度入力してください",
    )

    class Meta:
        model = User
        fields = (
            "employee_id",
            "username",
            "email",
            "is_admin",
            "is_staff",
            "is_active",
        )

    def clean_password2(self):
        """パスワード一致確認"""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("パスワードが一致しません")

        if password1 and len(password1) < 8:
            raise forms.ValidationError("パスワードは8文字以上で入力してください")

        return password2

    def save(self, commit=True):
        """パスワードをハッシュ化して保存"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user


class UserChangeForm(forms.ModelForm):
    """管理画面でのユーザー編集フォーム"""

    password = ReadOnlyPasswordHashField(
        label="パスワード",
        help_text=(
            "パスワードは暗号化されて保存されます。"
            '<a href="../password/">このフォーム</a>から変更できます。'
        ),
    )

    class Meta:
        model = User
        fields = (
            "employee_id",
            "username",
            "email",
            "password",
            "is_active",
            "is_admin",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    """ユーザー管理画面"""

    form = UserChangeForm
    add_form = UserCreationForm

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
