# accounts/permissions.py
"""
カスタムパーミッションクラス

is_adminフラグで管理者権限をチェック
レガシーシステムに最適化されたシンプルな権限管理
"""

from rest_framework.permissions import BasePermission


# ========================================
# 管理者専用パーミッション
# ========================================


class IsAdmin(BasePermission):
    """
    管理者権限チェック

    ユーザーが以下の条件を満たす場合のみアクセス許可:
    - 認証済み（is_authenticated = True）
    - 管理者フラグ（is_admin = True）

    Usage:
        permission_classes = [IsAuthenticated, IsAdmin]
    """

    message = "管理者権限が必要です"
    code = "admin_required"

    def has_permission(self, request, view):
        """
        グローバルパーミッションチェック

        ビュー全体へのアクセス可否を判定
        """
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_admin", False)
        )

    def has_object_permission(self, request, view, obj):
        """
        オブジェクトレベルパーミッションチェック

        特定のオブジェクトへのアクセス可否を判定
        """
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_admin", False)
        )


# ========================================
# 読み取り専用パーミッション
# ========================================


class IsAdminOrReadOnly(BasePermission):
    """
    管理者は全操作OK、一般ユーザーは読み取りのみ

    権限ルール:
    - GET, HEAD, OPTIONS: 認証済みなら誰でもOK
    - POST, PUT, PATCH, DELETE: 管理者のみOK

    Usage:
        permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    """

    message = "書き込み操作には管理者権限が必要です"
    code = "admin_required_for_write"

    def has_permission(self, request, view):
        """
        グローバルパーミッションチェック
        """
        # 安全なメソッド（読み取り）なら認証済みでOK
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return bool(request.user and request.user.is_authenticated)

        # 書き込みメソッドは管理者のみ
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_admin", False)
        )

    def has_object_permission(self, request, view, obj):
        """
        オブジェクトレベルパーミッションチェック
        """
        # 読み取りなら認証済みでOK
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return bool(request.user and request.user.is_authenticated)

        # 書き込みは管理者のみ
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_admin", False)
        )


# ========================================
# 使用例
# ========================================
"""
# ========================================
# 管理者専用API
# ========================================

class AdminUserListView(APIView):
    '''ユーザー一覧（管理者のみ）'''
    
    permission_classes = [IsAuthenticated, IsAdmin]
    authentication_classes = [CSRFEnforcedSessionAuthentication]
    
    def get(self, request):
        from common.models import User
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class AdminUserDeleteView(APIView):
    '''ユーザー削除（管理者のみ）'''
    
    permission_classes = [IsAuthenticated, IsAdmin]
    authentication_classes = [CSRFEnforcedSessionAuthentication]
    
    def delete(self, request, user_id):
        from common.models import User
        
        # 自分自身は削除できない
        if request.user.user_id == user_id:
            return Response(
                {'detail': '自分自身は削除できません'},
                status=400
            )
        
        user = User.objects.get(user_id=user_id)
        user.delete()
        
        return Response(status=204)


# ========================================
# 読み取り専用API
# ========================================

class ProductManageView(APIView):
    '''商品管理（管理者: 編集可、一般: 読み取りのみ）'''
    
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    authentication_classes = [CSRFEnforcedSessionAuthentication]
    
    def get(self, request):
        # 認証済みなら誰でもOK
        from products.models import Product
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # 管理者のみOK
        from products.models import Product
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)
    
    def put(self, request, pk):
        # 管理者のみOK
        from products.models import Product
        product = Product.objects.get(pk=pk)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def delete(self, request, pk):
        # 管理者のみOK
        from products.models import Product
        product = Product.objects.get(pk=pk)
        product.delete()
        return Response(status=204)


# ========================================
# 一般ユーザーもアクセス可能なAPI
# ========================================

class ShopProductListView(APIView):
    '''店頭商品一覧（一般ユーザー）'''
    
    permission_classes = [IsAuthenticated]  # 管理者チェックなし
    authentication_classes = [CSRFEnforcedSessionAuthentication]
    
    def get(self, request):
        from products.models import Product
        products = Product.objects.filter(is_active=True)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
"""
