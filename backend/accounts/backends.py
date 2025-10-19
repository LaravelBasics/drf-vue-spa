"""
カスタム認証バックエンド（複数削除済みユーザー対応版）

このファイルの役割:
- デフォルトの「username」ではなく「employee_id（社員番号）」でログイン
- パスワードの検証を行う
- 複数の削除済みユーザーが同じ社員番号を持っている場合に対応 ⭐
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

# カスタムユーザーモデルを取得（settings.AUTH_USER_MODEL で指定）
User = get_user_model()


class EmployeeIdBackend(BaseBackend):
    """
    社員番号（employee_id）でログインするための認証バックエンド

    処理の流れ:
    1. 社員番号でユーザーを検索（アクティブなユーザー優先）⭐
    2. パスワードが一致するか確認
    3. 一致すればユーザー情報を返す

    注意:
    - 削除済み・無効化されたユーザーの判定は views.py で行う
    - ここでは認証のみを担当
    - 複数の削除済みユーザーがいても正しく動作 ⭐
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        社員番号とパスワードで認証

        引数:
            request: HTTPリクエスト（未使用だが必須）
            username: 社員番号（Django内部では username と呼ばれる）
            password: パスワード

        戻り値:
            User: 認証成功時
            None: 認証失敗時

        ⭐ 変更点:
        - get() → filter().first() に変更
        - アクティブなユーザーを優先的に取得
        - 複数の削除済みユーザーがいても最新のものを取得
        """

        # わかりやすいように変数名を変更
        employee_id = username

        # 社員番号またはパスワードが未入力なら失敗
        if not employee_id or not password:
            return None

        try:
            # ⭐ 改善: 複数ユーザーがいても正常に動作
            # 優先順位:
            # 1. アクティブなユーザー（deleted_at が NULL）
            # 2. 削除済みユーザー（最新のもの）

            # アクティブなユーザーを最優先で検索
            user = User.objects.filter(employee_id=employee_id).first()

            # アクティブなユーザーがいない場合、削除済みから検索
            if not user:
                user = (
                    User.all_objects.filter(employee_id=employee_id)
                    .order_by("-created_at")
                    .first()
                )  # 最新の削除済みユーザー

            # ユーザーが見つからない場合
            if not user:
                # セキュリティ対策: タイミング攻撃を防ぐため、
                # 存在しないユーザーでもパスワード処理を実行
                # （処理時間から「ユーザーの存在」を推測されないようにする）
                User().set_password(password)
                return None

        except Exception as e:
            # 予期しないエラーの場合もセキュリティ対策
            User().set_password(password)
            return None

        # パスワードが一致するか確認
        if user.check_password(password):
            return user

        # パスワード不一致
        return None

    def get_user(self, user_id):
        """
        セッションからログインユーザーを取得

        役割:
        - ページ遷移時に「このユーザーはログイン済みか」を確認
        - セッション（Cookie）に保存されたユーザーIDから情報を取得

        引数:
            user_id: セッションに保存されているユーザーID

        戻り値:
            User: ユーザー情報
            None: ユーザーが存在しない（削除済み）
        """
        try:
            # 削除されていないユーザーのみ取得
            # 削除済みユーザーは自動的にログアウトされる
            return User.objects.get(pk=user_id)

        except User.DoesNotExist:
            return None


# ==================== 変更点のまとめ ====================
"""
✅ 修正内容:

1. get() → filter().first() に変更
   ❌ 旧: user = User.all_objects.get(employee_id=employee_id)
       → 複数ヒット時に MultipleObjectsReturned エラー
   
   ✅ 新: user = User.objects.filter(employee_id=employee_id).first()
       → 複数いても最初の1件を取得（エラーにならない）

2. 検索の優先順位を明確化
   ① User.objects（アクティブなユーザーのみ）
   ② User.all_objects（削除済みも含む）で最新のものを取得

3. 例外処理を追加
   - 予期しないエラーでもセキュリティ対策を実行


動作パターン:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

パターン1: アクティブなユーザーが1人
├─ employee_id: 777, deleted_at: NULL
└─ → このユーザーで認証

パターン2: 削除済みユーザーが1人
├─ employee_id: 777, deleted_at: 2025-01-19
└─ → このユーザーで認証 → views.py で「削除済み」エラー

パターン3: 削除済みユーザーが3人 ⭐
├─ employee_id: 777, deleted_at: 2025-01-19, created_at: 2024-01-01
├─ employee_id: 777, deleted_at: 2025-01-19, created_at: 2024-06-01
└─ employee_id: 777, deleted_at: 2025-01-19, created_at: 2024-12-01
    └─ → 最新（2024-12-01）のユーザーで認証 → views.py で「削除済み」エラー

パターン4: アクティブ1人 + 削除済み3人 ⭐
├─ employee_id: 777, deleted_at: NULL, created_at: 2025-01-19  ← 優先
├─ employee_id: 777, deleted_at: 2025-01-18, created_at: 2024-01-01
├─ employee_id: 777, deleted_at: 2025-01-18, created_at: 2024-06-01
└─ employee_id: 777, deleted_at: 2025-01-18, created_at: 2024-12-01
    └─ → アクティブなユーザーで認証（削除済みは無視）


検索ロジックの詳細:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. まずアクティブなユーザーを検索
   User.objects.filter(employee_id=employee_id).first()
   → deleted_at が NULL のユーザーのみ
   → アクティブなユーザーがいればそれを返す

2. アクティブなユーザーがいない場合
   User.all_objects.filter(employee_id=employee_id).order_by('-created_at').first()
   → 削除済みも含めて検索
   → created_at が最新のユーザーを返す
   → 最新の削除済みユーザーを取得

3. それでも見つからない場合
   → None を返す
   → セキュリティ対策（タイミング攻撃防止）


セキュリティ考慮:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- タイミング攻撃対策
  ユーザーが存在しない場合でも User().set_password(password) を実行
  → 処理時間から「ユーザーの存在」を推測されないようにする

- 例外処理
  予期しないエラーが発生しても適切に対処
  → システムの安定性を保つ


使用例:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ケース1: 社員番号777でログイン（アクティブユーザーあり）
authenticate(request, username='777', password='test1234')
→ アクティブなユーザーを返す
→ views.py でログイン成功

# ケース2: 社員番号777でログイン（削除済み3人のみ）
authenticate(request, username='777', password='test1234')
→ 最新の削除済みユーザーを返す
→ views.py で「このアカウントは削除されています」エラー

# ケース3: 存在しない社員番号でログイン
authenticate(request, username='999', password='test1234')
→ None を返す
→ views.py で「社員番号またはパスワードが正しくありません」エラー
"""
