# backend/users/permissions.py
"""
ユーザー管理の権限チェック

このファイルの役割:
- APIにアクセスできるユーザーを制限する
- 「管理者のみアクセスOK」などの権限ルールを定義

なぜ必要？:
- すべてのユーザーがユーザー管理できると危険
- 管理者だけが使える機能を制限したい
"""

from rest_framework import permissions


# ==================== 管理者専用 ====================

class IsAdminUser(permissions.BasePermission):
    """
    管理者のみアクセスを許可する権限クラス
    
    誰がアクセスできる？:
    - is_admin=True のユーザーのみ
    
    アクセスできない場合のエラー:
    - 未ログイン → 401 Unauthorized（ログインしてください）
    - ログイン済みだが管理者でない → 403 Forbidden（権限がありません）
    
    使い方:
    class UserViewSet(viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated, IsAdminUser]
        # ↑ ログイン済み かつ 管理者 のみアクセスOK
    """
    
    # エラーメッセージ（403エラー時に表示される）
    message = '管理者権限が必要です'
    
    def has_permission(self, request, view):
        """
        APIにアクセスする権限があるかチェック
        
        引数:
            request: リクエスト情報
            view: アクセスしようとしているビュー
        
        戻り値:
            True: アクセスOK
            False: アクセス拒否
        """
        # ① まずログインチェック
        if not request.user or not request.user.is_authenticated:
            return False  # 未ログイン → 401エラー
        
        # ② 管理者チェック
        return request.user.is_admin  # True なら OK, False なら 403エラー
    
    def has_object_permission(self, request, view, obj):
        """
        特定のデータ（オブジェクト）にアクセスする権限があるかチェック
        
        このメソッドが呼ばれるタイミング:
        - 個別のユーザー情報を取得・更新・削除する時
        - 例: GET /api/users/5/
        
        引数:
            request: リクエスト情報
            view: アクセスしようとしているビュー
            obj: アクセス対象のオブジェクト（ユーザーなど）
        
        戻り値:
            True: アクセスOK
            False: アクセス拒否
        """
        # 管理者ならすべてのユーザー情報にアクセスOK
        return request.user.is_admin


# ==================== 管理者は全操作OK、一般ユーザーは閲覧のみ ====================

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    管理者は全操作OK、一般ユーザーは読み取り専用
    
    誰が何をできる？:
    - 管理者: すべての操作（作成・更新・削除）ができる
    - 一般ユーザー: 閲覧のみ（GET）
    
    使い方:
    class ProductViewSet(viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
        # ↑ 管理者: CRUD全部OK
        #    一般ユーザー: 一覧・詳細の閲覧のみOK
    """
    
    message = 'この操作には管理者権限が必要です'
    
    def has_permission(self, request, view):
        """権限チェック"""
        # ① ログインチェック
        if not request.user or not request.user.is_authenticated:
            return False
        
        # ② GET（閲覧）なら全員OK
        # SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # ③ POST・PUT・DELETE は管理者のみ
        return request.user.is_admin


# ==================== 使用例 ====================
"""
views.py での使い方:

# パターン1: 管理者専用API
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    # ↑ ログイン済み + 管理者のみ

# パターン2: 閲覧は全員OK、編集は管理者のみ
class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    # ↑ 管理者: CRUD全部OK
    #    一般ユーザー: GET のみOK
"""