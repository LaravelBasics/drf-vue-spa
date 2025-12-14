"""
Django プロジェクト設定ファイル

注意: 本番環境ではSECRET_KEY、DEBUGを環境変数で管理すること
"""

from pathlib import Path
from django.utils.translation import gettext_lazy as _
import os
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
# ⭐ .env ファイルを読み込み
load_dotenv(BASE_DIR / ".env")

# === セキュリティ ===

# ⭐ 環境変数から読み込む
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-fallback-key")

# ⭐ DEBUG も環境変数化
DEBUG = os.getenv("DEBUG", "False") == "True"

# ⭐ ALLOWED_HOSTS も環境変数化
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# === アプリケーション ===

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "django_filters",
    "accounts",
    # "users",
    "common",  # モデルアプリ（inspectdb取り込み）
    # "debug_toolbar",  # 開発ツール（最後に追加）
]

# === 認証 ===

# AUTH_USER_MODEL = "users.User"
# ========================================
# カスタムユーザーモデル（★超重要★）
# ========================================
AUTH_USER_MODEL = "common.MUser"

AUTHENTICATION_BACKENDS = [
    "accounts.backends.GroupUserAuthBackend",  # カスタムバックエンド
]

# === REST Framework ===

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

# === ミドルウェア ===

MIDDLEWARE = [
    # "debug_toolbar.middleware.DebugToolbarMiddleware",  # ← 先頭付近に追加
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "common.middleware.LanguageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "common.middleware.AuditMiddleware",  # 監査ミドルウェア
    # "querycount.middleware.QueryCountMiddleware",  # ← どこでもOK
]

# === キャッシュ ===

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# === CORS ===

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

# ✅ Content-Dispositionを公開
CORS_EXPOSE_HEADERS = [
    "Content-Disposition",
]

CORS_ALLOW_CREDENTIALS = True

# === セッション ===

SESSION_COOKIE_AGE = 86400
# ブラウザを閉じたらセッションを破棄する設定
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = False  # DB負荷考慮
SESSION_COOKIE_SECURE = False  # 本番ではNG

# 本番設定
# SESSION_COOKIE_HTTPONLY = True  # ✅ 必須
# SESSION_COOKIE_SECURE = True  # ✅ 必須
# SESSION_COOKIE_SAMESITE = "Lax"  # ✅ 推奨
# CSRF_COOKIE_HTTPONLY = False  # ✅ 必須（JSから読む）
# CSRF_COOKIE_SECURE = True  # ✅ 必須
# CSRF_COOKIE_SAMESITE = "Lax"  # ✅ 推奨

# === CSRF ===

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
]
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False  # 本番はTrue

# === URL設定 ===

ROOT_URLCONF = "config.urls"

# === テンプレート ===

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# === WSGI ===

WSGI_APPLICATION = "config.wsgi.application"

# === データベース ===

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "your_db_name"),
        "USER": os.getenv("DB_USER", "your_username"),
        "PASSWORD": os.getenv("DB_PASSWORD", "your_password"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "OPTIONS": {
            # DjangoがSQLを実行する際に、この検索パスを設定します。
            "options": "-c search_path=legacy_schema,public",
        },
    }
}

# === パスワード検証 ===

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# === パスワードハッシュアルゴリズム ===
PASSWORD_HASHERS = [
    # "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",  # ★Django標準（追加パッケージ不要）★
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",  # レガシー互換用
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# === ログイン設定 ===

LOGIN_MAX_ATTEMPTS = int(os.getenv("LOGIN_MAX_ATTEMPTS", "10"))
LOGIN_LOCKOUT_DURATION = int(os.getenv("LOGIN_LOCKOUT_DURATION", "60"))

# === 国際化 ===

LANGUAGES = [
    ("ja", _("日本語")),
    ("en", _("English")),
]

LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# === 静的ファイル ===

STATIC_URL = "static/"

# === デフォルト設定 ===

# DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# === システムチェック ===

# カスタムユーザーモデルで is_superuser フィールドがない警告を抑制
# (ビジネス要件に従い is_admin を使用しているため)
# SILENCED_SYSTEM_CHECKS = ["auth.W004"]

# === 監査ログ設定 ===

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,  # 既存のログを無効化しない
#     "formatters": {
#         "verbose": {
#             "format": "{levelname} {asctime} {module} {message}",
#             "style": "{",
#         },
#         "audit_json": {
#             "()": "common.formatters.AuditJSONFormatter",
#             "datefmt": "%Y-%m-%d %H:%M:%S",
#         },
#     },
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#             "formatter": "verbose",
#         },
#         "audit_file": {
#             "level": "INFO",
#             "class": "logging.handlers.RotatingFileHandler",
#             "filename": BASE_DIR / "logs" / "audit.log",
#             "maxBytes": 10 * 1024 * 1024,  # 10MB
#             "backupCount": 30,  # 過去30ファイル保持
#             "formatter": "audit_json",
#             "encoding": "utf-8",
#         },
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["console"],
#             "level": "INFO",
#         },
#         "audit": {
#             "handlers": ["audit_file"],
#             "level": "INFO",
#             "propagate": False,  # 親ロガーに伝播させない
#         },
#     },
# }

# Debug Toolbar設定（最後に追加）
# INTERNAL_IPS = [
#     "127.0.0.1",
# ]

# querycount設定（最後に追加）
# QUERYCOUNT = {
#     "THRESHOLDS": {
#         "MEDIUM": 50,
#         "HIGH": 200,
#         "MIN_TIME_TO_LOG": 0,
#         "MIN_QUERY_COUNT_TO_LOG": 0,
#     },
#     "IGNORE_REQUEST_PATTERNS": [],
#     "IGNORE_SQL_PATTERNS": [],
#     "DISPLAY_DUPLICATES": 10,
#     "RESPONSE_HEADER": "X-DjangoQueryCount-Count",
# }


# ========================================
# レガシーシステム運用メモ
# ========================================
"""
【inspectdb運用ルール】

1. テーブル管理
   - PostgreSQL側で管理（ALTER TABLE等）
   - Djangoマイグレーションは使わない（managed=False）

2. モデル更新手順
   - PostgreSQLでテーブル変更
   - python manage.py inspectdb > temp_models.py
   - 手動でmodels.pyに反映（認証メソッドは維持）

3. 初回セットアップ
   - PostgreSQLに以下のテーブルを作成:
     * m_user (user_id PK, password, username, email, is_admin, is_active)
     * m_group (group_id PK, group_name, is_active)
     * m_user_group (user_id, group_id, is_active)
   - Djangoのsessionテーブルは標準マイグレーションで作成:
     * python manage.py migrate

4. パスワードハッシュ化
   - 既存ユーザーのパスワードをDjango形式にハッシュ化:
     ```python
     from django.contrib.auth.hashers import make_password
     hashed = make_password('your_password')
     # PostgreSQLのpasswordカラムに保存
     ```

5. 管理者権限設定
   - PostgreSQLで特定ユーザーを管理者に:
     ```sql
     UPDATE m_user SET is_admin = TRUE WHERE user_id = 'admin001';
     ```

6. トラブルシューティング
   - User.DoesNotExist → user_idの型確認（文字列 vs 整数）
   - IsAuthenticated動かない → models.pyのメソッド確認
   - CSRF failed → CSRFEnforcedSessionAuthentication確認
   - 管理者権限チェック失敗 → is_adminカラム確認
"""
