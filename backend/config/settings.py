# backend/config/settings.py
"""
Django プロジェクトの設定ファイル

このファイルの役割:
- Django の動作を制御する設定をまとめる
- データベース、認証、セキュリティなどの設定

注意:
- 本番環境では SECRET_KEY や DEBUG を環境変数で管理すること
- このファイルは Git にコミットしても良いが、機密情報は .env で管理
"""

from pathlib import Path

# ==================== 基本設定 ====================

# プロジェクトのルートディレクトリ
# 例: /home/user/project/backend/
BASE_DIR = Path(__file__).resolve().parent.parent


# ==================== セキュリティ設定 ====================

# シークレットキー（暗号化に使用）
# ⚠️ 本番環境では環境変数で管理すること
SECRET_KEY = 'django-insecure-ycbc+50@xd3u8)6tsw27*q6!uz2l2asg0-$wdgs^j99wokh1w@'

# デバッグモード
# True: 開発環境（エラーの詳細が表示される）
# False: 本番環境（エラーの詳細は非表示）
DEBUG = True

# アクセスを許可するホスト
# 本番環境では ['example.com', 'www.example.com'] のように指定
ALLOWED_HOSTS = []


# ==================== インストール済みアプリ ====================

INSTALLED_APPS = [
    # ==================== Django標準アプリ ====================
    "django.contrib.admin",        # 管理画面（/admin/）
    "django.contrib.auth",         # 認証システム
    "django.contrib.contenttypes", # コンテンツタイプ（権限管理の基盤）
    "django.contrib.sessions",     # セッション管理（Cookieでログイン状態を保持）
    "django.contrib.messages",     # フラッシュメッセージ（一時的な通知）
    "django.contrib.staticfiles",  # 静的ファイル管理（CSS, JS, 画像）
    
    # ==================== サードパーティ ====================
    "rest_framework",              # REST API フレームワーク
    "corsheaders",                 # CORS対応（フロントエンドとの通信）
    "django_filters",              # フィルター機能（検索・絞り込み）
    
    # ==================== 自作アプリ ====================
    "accounts",                    # 認証専用（ログイン/ログアウト）
    "users",                       # ユーザー管理（CRUD）
]


# ==================== カスタムユーザーモデル ====================

# デフォルトのユーザーモデルを置き換え
# 'users.User' = users アプリの User モデルを使用
AUTH_USER_MODEL = 'users.User'


# ==================== 認証バックエンド ====================

# ログイン認証の方法を指定
AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmployeeIdBackend',  # 社員番号でログイン（カスタム）
    # 'django.contrib.auth.backends.ModelBackend',  # デフォルト（username でログイン）
]


# ==================== REST Framework 設定 ====================

REST_FRAMEWORK = {
    # ==================== 認証方法 ====================
    # APIを叩いた時に「誰がアクセスしているか」を判定する方法
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # SessionAuthentication = Cookie（セッション）で認証
        # ログイン後はブラウザの Cookie に情報が保存される
        "rest_framework.authentication.SessionAuthentication",
    ],
    
    # ==================== デフォルト権限 ====================
    # 認証されていないユーザーのアクセスを制限
    "DEFAULT_PERMISSION_CLASSES": [
        # IsAuthenticated = ログイン済みユーザーのみアクセスOK
        # AllowAny に変更すると誰でもアクセスできる
        "rest_framework.permissions.IsAuthenticated",
    ],
    
    # ==================== ページネーション ====================
    # 一覧APIで大量データを分割して返す
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # 1ページあたり10件
    
    # ==================== フィルター・検索・並び替え ====================
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',  # フィルター（is_admin=true など）
        'rest_framework.filters.SearchFilter',                # 検索（キーワード検索）
        'rest_framework.filters.OrderingFilter',              # 並び替え（作成日順など）
    ],
}


# ==================== ミドルウェア ====================

# リクエスト処理の順番（上から順に実行される）
MIDDLEWARE = [
    # ==================== CORS（フロントエンドとの通信） ====================
    # 一番上に配置すること（他のミドルウェアより先に実行）
    "corsheaders.middleware.CorsMiddleware",
    
    # ==================== Django標準ミドルウェア ====================
    'django.middleware.security.SecurityMiddleware',      # セキュリティ対策
    'django.contrib.sessions.middleware.SessionMiddleware',  # セッション管理
    'django.middleware.common.CommonMiddleware',          # 共通処理
    'django.middleware.csrf.CsrfViewMiddleware',          # CSRF対策
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 認証処理
    'django.contrib.messages.middleware.MessageMiddleware',     # メッセージ処理
    'django.middleware.clickjacking.XFrameOptionsMiddleware',   # クリックジャッキング対策
]


# ==================== キャッシュ設定 ====================

# ブルートフォース攻撃対策のログイン失敗回数を記録
CACHES = {
    'default': {
        # LocMemCache = メモリにキャッシュ（開発環境用）
        # 本番環境では Redis を推奨:
        # 'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        # 'LOCATION': 'redis://127.0.0.1:6379/1',
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}


# ==================== CORS設定（フロントエンドとの通信） ====================

# すべてのオリジンを許可するか
# False = 特定のURLのみ許可（推奨）
CORS_ALLOW_ALL_ORIGINS = False

# 許可するフロントエンドのURL
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vue.js 開発サーバー（Vite）
    # "http://localhost:3000",  # React 開発サーバー
]

# Cookie を含むリクエストを許可
# True = セッション認証が使える
CORS_ALLOW_CREDENTIALS = True


# ==================== セッション設定 ====================

# セッションの有効期限（秒）
# 86400秒 = 24時間 = 1日
SESSION_COOKIE_AGE = 86400

# ブラウザを閉じてもセッションを維持
# False = ブラウザを閉じてもログイン状態を保持
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# アクティビティがあればセッションを延長
# True = APIを叩くたびにセッションの有効期限がリセットされる
SESSION_SAVE_EVERY_REQUEST = True

# セッション Cookie をHTTPSのみに制限
# False = HTTP でも OK（開発環境）
# True = HTTPS のみ（本番環境）
SESSION_COOKIE_SECURE = False


# ==================== CSRF設定（セキュリティ） ====================

# CSRF トークンを信頼するオリジン
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",  # Vue.js 開発サーバー
]

# CSRF Cookie を JavaScript から読み取り可能にする
# False = JavaScript から読み取れる（フロントエンドが必要）
# True = JavaScript から読み取れない（より安全）
CSRF_COOKIE_HTTPONLY = False

# CSRF Cookie をHTTPSのみに制限
# False = HTTP でも OK（開発環境）
# True = HTTPS のみ（本番環境）
CSRF_COOKIE_SECURE = False


# ==================== URL設定 ====================

# メインのURL設定ファイル
ROOT_URLCONF = 'config.urls'


# ==================== テンプレート設定 ====================

# HTML テンプレートの設定（Django管理画面で使用）
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # カスタムテンプレートディレクトリ（必要に応じて追加）
        'APP_DIRS': True,  # 各アプリの templates/ を自動検索
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ==================== WSGI設定 ====================

# 本番環境で使用する WSGI アプリケーション
WSGI_APPLICATION = 'config.wsgi.application'


# ==================== データベース設定 ====================

DATABASES = {
    'default': {
        # SQLite（開発環境用）
        # 本番環境では PostgreSQL や MySQL を推奨:
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': 'your_db_name',
        # 'USER': 'your_db_user',
        # 'PASSWORD': 'your_db_password',
        # 'HOST': 'localhost',
        # 'PORT': '5432',
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ==================== パスワード検証 ====================

# パスワードの強度チェック
AUTH_PASSWORD_VALIDATORS = [
    # ユーザー名とパスワードが似ていないかチェック
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    # 最小文字数チェック（デフォルト: 8文字）
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    # よくあるパスワード（password123 など）をチェック
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    # 数字だけのパスワードを禁止
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ==================== 国際化（i18n）設定 ====================

# 言語コード
LANGUAGE_CODE = 'ja'  # 日本語

# タイムゾーン
TIME_ZONE = 'Asia/Tokyo'  # 日本時間（JST）

# 国際化を有効化
USE_I18N = True

# タイムゾーンを有効化
# True = データベースに UTC で保存し、表示時に変換
USE_TZ = True


# ==================== 静的ファイル設定 ====================

# 静的ファイル（CSS, JS, 画像）のURL
STATIC_URL = 'static/'

# 本番環境での静的ファイル収集先
# python manage.py collectstatic で収集
# STATIC_ROOT = BASE_DIR / 'staticfiles'


# ==================== デフォルト設定 ====================

# 主キー（ID）のデフォルトフィールドタイプ
# BigAutoField = 大きな数字まで扱える自動採番ID
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==================== 本番環境での追加設定例 ====================
"""
本番環境では以下の設定を追加すること:

import os

# 環境変数から読み込み
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = ['example.com', 'www.example.com']

# データベースをPostgreSQLに変更
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': '5432',
    }
}

# キャッシュをRedisに変更
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# セキュリティ強化
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
"""