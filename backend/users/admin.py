# backend/users/admin.py
"""
Django管理画面のカスタマイズ

このファイルの役割:
- /admin/ でユーザーを管理できるようにする
- 一覧画面・詳細画面のカスタマイズ
- 削除済みユーザーの表示・復元機能

Django管理画面とは:
- Django が標準で提供する管理ツール
- http://localhost:8000/admin/ でアクセス
- スーパーユーザーのみログイン可能
"""

from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)  # この行で User モデルを管理画面に登録
class CustomUserAdmin(admin.ModelAdmin):
    """ユーザー管理画面のカスタマイズ"""
    
    # ==================== 一覧画面の設定 ====================
    
    # 一覧画面に表示する項目
    list_display = [
        'employee_id',   # 社員番号
        'username',      # ユーザー名
        'email',         # メールアドレス
        'is_admin',      # 管理者フラグ
        'is_active',     # アクティブフラグ
        'is_deleted',    # 削除済みフラグ（カスタムメソッド）
        'created_at'     # 作成日時
    ]
    
    # 絞り込み（フィルター）機能
    # 右側に表示されるフィルターパネル
    list_filter = [
        'is_admin',      # 管理者で絞り込み
        'is_active',     # アクティブで絞り込み
        'is_staff',      # スタッフで絞り込み
        'created_at',    # 作成日で絞り込み
        'deleted_at',    # 削除日で絞り込み
    ]
    
    # 検索機能（上部の検索ボックス）
    search_fields = ['employee_id', 'username', 'email']
    
    # デフォルトの並び順（新しい順）
    ordering = ['-created_at']
    
    # ==================== 詳細画面の設定 ====================
    
    # 詳細画面のフィールドをグループ分け
    fieldsets = (
        # グループ1: 認証情報
        ('認証情報', {
            'fields': ('employee_id', 'password')
        }),
        # グループ2: 個人情報
        ('個人情報', {
            'fields': ('username', 'email')
        }),
        # グループ3: 権限設定
        ('権限', {
            'fields': (
                'is_active',        # アクティブ
                'is_admin',         # 管理者
                'is_staff',         # スタッフ（管理画面ログインOK）
                'is_superuser',     # スーパーユーザー（全権限）
                'groups',           # グループ
                'user_permissions', # 個別権限
            )
        }),
        # グループ4: タイムスタンプ（折りたたみ表示）
        ('タイムスタンプ', {
            'fields': ('created_at', 'updated_at', 'deleted_at', 'last_login'),
            'classes': ('collapse',),  # 最初は折りたたまれている
        }),
    )
    
    # 新規作成時のフィールド（パスワード確認が必要）
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
    
    # 読み取り専用フィールド（編集不可）
    readonly_fields = ['created_at', 'updated_at', 'deleted_at', 'last_login']
    
    # ==================== カスタムメソッド ====================
    
    @admin.display(boolean=True, description='削除済み')
    def is_deleted(self, obj):
        """
        削除済みかどうかを表示するカスタム項目
        
        引数:
            obj: ユーザーオブジェクト
        
        戻り値:
            True: ✓ マークが表示される
            False: ✗ マークが表示される
        """
        return obj.deleted_at is not None
    
    # ==================== 一括アクション ====================
    
    # 使用可能なアクション（一覧画面の上部に表示）
    actions = ['restore_users', 'soft_delete_users']
    
    @admin.action(description='選択したユーザーを復元')
    def restore_users(self, request, queryset):
        """
        選択したユーザーを一括復元
        
        使い方:
        1. 一覧画面で復元したいユーザーにチェック
        2. アクション選択で「選択したユーザーを復元」を選ぶ
        3. 実行
        """
        count = 0
        for user in queryset:
            # 削除済みユーザーのみ復元
            if user.deleted_at:
                user.restore()  # models.py の restore メソッド
                count += 1
        
        # 完了メッセージを表示
        self.message_user(request, f'{count}人のユーザーを復元しました。')
    
    @admin.action(description='選択したユーザーを論理削除')
    def soft_delete_users(self, request, queryset):
        """
        選択したユーザーを一括論理削除
        
        使い方:
        1. 一覧画面で削除したいユーザーにチェック
        2. アクション選択で「選択したユーザーを論理削除」を選ぶ
        3. 実行
        """
        count = 0
        for user in queryset:
            # 未削除のユーザーのみ削除
            if not user.deleted_at:
                user.soft_delete()  # models.py の soft_delete メソッド
                count += 1
        
        # 完了メッセージを表示
        self.message_user(request, f'{count}人のユーザーを論理削除しました。')
    
    # ==================== 追加設定 ====================
    
    def get_queryset(self, request):
        """
        一覧に表示するユーザーを取得
        
        通常は削除済みユーザーは表示されないが、
        管理画面では削除済みも含めてすべて表示する
        """
        return User.all_objects.all()  # 削除済みも含む
    
    def get_form(self, request, obj=None, **kwargs):
        """
        編集フォームをカスタマイズ
        
        新規作成と編集で異なるフィールドセットを使う
        
        引数:
            obj: 編集対象のユーザー（None なら新規作成）
        """
        if obj is None:
            # 新規作成時: password1, password2 を使う
            self.fieldsets = self.add_fieldsets
        else:
            # 編集時: 通常のフィールドセット
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
        """
        ユーザーを保存する時の処理
        
        パスワードをハッシュ化して保存
        
        引数:
            request: リクエスト情報
            obj: 保存するユーザーオブジェクト
            form: フォームデータ
            change: True=編集, False=新規作成
        """
        if not change:
            # 新規作成時: password1 をハッシュ化
            obj.set_password(form.cleaned_data['password1'])
        elif 'password' in form.changed_data:
            # パスワード変更時: ハッシュ化
            obj.set_password(form.cleaned_data['password'])
        
        # 保存
        super().save_model(request, obj, form, change)


# ==================== 使い方まとめ ====================
"""
Django管理画面の使い方:

1. スーパーユーザーでログイン
   python manage.py createsuperuser

2. 管理画面にアクセス
   http://localhost:8000/admin/

3. できること:
   - ユーザー一覧の表示（削除済みも含む）
   - ユーザーの検索・絞り込み
   - ユーザーの作成・編集・削除
   - 削除済みユーザーの復元
   - 一括操作（複数選択して削除・復元）
"""