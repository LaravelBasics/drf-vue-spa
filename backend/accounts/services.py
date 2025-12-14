# accounts/services.py
"""
認証サービスクラス

責務:
- ログイン試行回数の管理
- アカウントロック処理
- ブルートフォース攻撃対策
- グループ管理
- ユーザー所属グループ管理
"""

from django.core.cache import cache
from django.conf import settings


# ========================================
# ログイン試行管理サービス
# ========================================


class LoginAttemptService:
    """
    ログイン試行管理サービス

    機能:
    - 失敗回数のカウント
    - アカウントロック/アンロック
    - グループ単位での管理
    """

    # キャッシュキーのプレフィックス
    ATTEMPT_KEY_PREFIX = "login_attempts"
    LOCKOUT_KEY_PREFIX = "login_locked"

    @classmethod
    def get_cache_key(cls, user_id, group_id):
        """
        ログイン試行回数のキャッシュキーを生成

        Args:
            user_id: ユーザーID
            group_id: グループID

        Returns:
            str: キャッシュキー
        """
        return f"{cls.ATTEMPT_KEY_PREFIX}:{group_id}:{user_id}"

    @classmethod
    def get_lockout_key(cls, user_id, group_id):
        """
        アカウントロックのキャッシュキーを生成

        Args:
            user_id: ユーザーID
            group_id: グループID

        Returns:
            str: ロックキー
        """
        return f"{cls.LOCKOUT_KEY_PREFIX}:{group_id}:{user_id}"

    @classmethod
    def increment_attempts(cls, user_id, group_id):
        """
        ログイン失敗回数をインクリメント

        Args:
            user_id: ユーザーID
            group_id: グループID

        Returns:
            int: 現在の失敗回数
        """
        key = cls.get_cache_key(user_id, group_id)
        attempts = cache.get(key, 0) + 1

        # 1時間キャッシュ
        cache.set(key, attempts, 3600)
        return attempts

    @classmethod
    def get_attempts(cls, user_id, group_id):
        """
        現在のログイン失敗回数を取得

        Args:
            user_id: ユーザーID
            group_id: グループID

        Returns:
            int: 失敗回数
        """
        key = cls.get_cache_key(user_id, group_id)
        return cache.get(key, 0)

    @classmethod
    def is_locked(cls, user_id, group_id):
        """
        アカウントがロック中か確認

        Args:
            user_id: ユーザーID
            group_id: グループID

        Returns:
            bool: ロック中ならTrue
        """
        key = cls.get_lockout_key(user_id, group_id)
        return cache.get(key, False)

    @classmethod
    def lock_user(cls, user_id, group_id):
        """
        アカウントをロック

        Args:
            user_id: ユーザーID
            group_id: グループID
        """
        key = cls.get_lockout_key(user_id, group_id)
        lockout_duration = getattr(settings, "LOGIN_LOCKOUT_DURATION")
        cache.set(key, True, lockout_duration)

    @classmethod
    def reset_attempts(cls, user_id, group_id):
        """
        ログイン失敗回数とロックをリセット

        Args:
            user_id: ユーザーID
            group_id: グループID
        """
        cache.delete(cls.get_cache_key(user_id, group_id))
        cache.delete(cls.get_lockout_key(user_id, group_id))

    @classmethod
    def should_lock(cls, user_id, group_id):
        """
        ログイン失敗回数が上限に達したか確認

        Args:
            user_id: ユーザーID
            group_id: グループID

        Returns:
            bool: ロックすべきならTrue
        """
        attempts = cls.get_attempts(user_id, group_id)
        max_attempts = getattr(settings, "LOGIN_MAX_ATTEMPTS")
        return attempts >= max_attempts


# ========================================
# グループ管理サービス
# ========================================


class GroupService:
    """
    グループ関連サービス

    機能:
    - アクティブなグループ一覧取得
    - グループ存在確認
    """

    @staticmethod
    def get_active_groups():
        """
        アクティブなグループ一覧を取得

        Returns:
            QuerySet: アクティブなグループ
        """
        from common.models import MGroup

        return MGroup.objects.filter(is_active=True).order_by("group_id")

    @staticmethod
    def group_exists(group_id):
        """
        グループが存在するか確認

        Args:
            group_id: グループID

        Returns:
            bool: 存在すればTrue
        """
        from common.models import MGroup

        return MGroup.objects.filter(group_id=group_id, is_active=True).exists()


# ========================================
# ユーザー所属グループサービス
# ========================================


class UserGroupService:
    """
    ユーザー所属グループサービス

    機能:
    - ユーザーのグループ所属確認
    - グループ情報取得
    """

    @staticmethod
    def get_user_group_info(user_id, group_id):
        """
        ユーザーの所属グループ情報を取得

        Args:
            user_id: ユーザーID
            group_id: グループID

        Returns:
            dict or None: グループ情報 {group_id, group_name}
        """
        from common.models import MUserGroup, MGroup

        try:
            user_group = MUserGroup.objects.filter(
                user_id=user_id, group_id=group_id, is_active=True
            ).first()

            if not user_group:
                return None

            group = MGroup.objects.filter(
                group_id=user_group.group_id, is_active=True
            ).first()

            if not group:
                return None

            return {"group_id": group.group_id, "group_name": group.group_name}

        except Exception:
            return None

    @staticmethod
    def user_belongs_to_group(user_id, group_id):
        """
        ユーザーがグループに所属しているか確認

        Args:
            user_id: ユーザーID
            group_id: グループID

        Returns:
            bool: 所属していればTrue
        """
        from common.models import MUserGroup

        return MUserGroup.objects.filter(
            user_id=user_id, group_id=group_id, is_active=True
        ).exists()
