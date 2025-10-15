# backend/test_permission.py
"""
権限チェックのテストスクリプト

このファイルの役割:
- 一般ユーザーと管理者の権限をテスト
- APIに正しく権限制限がかかっているか確認

使い方:
1. ブラウザでログイン
2. F12 → Application → Cookies → sessionid をコピー
3. このファイルの session_id を更新
4. python test_permission.py

必要なライブラリ:
pip install requests
"""

import requests

# ==================== テストパターン1: 一般ユーザー ====================
"""
一般ユーザーでのテスト

手順:
1. ブラウザで一般ユーザーでログイン
2. F12キー → Application タブ → Cookies → sessionid をコピー
3. 下記の session_id に貼り付け
4. コメントアウトを外して実行

期待結果:
- ステータスコード: 403 Forbidden
- レスポンス: {'detail': '管理者権限が必要です'}
"""

# 一般ユーザーのセッションID（例）
# session_id = "i2lg4o8xjopbwjnl77h3ocfwdc7n2srk"

# headers = {
#     # 認証情報を 'Cookie' ヘッダーで渡す
#     "Cookie": f"sessionid={session_id}"
# }

# # ユーザー一覧取得を試みる
# response = requests.get(
#     "http://localhost:8000/api/users/",
#     headers=headers
# )

# print(f"ステータスコード: {response.status_code}")
# print(f"レスポンス: {response.json()}")

# 実行結果例:
# ステータスコード: 403
# レスポンス: {'detail': '管理者権限が必要です'}


# ==================== テストパターン2: 管理者 ====================
"""
管理者でのテスト

手順:
1. ブラウザで管理者アカウントでログイン
2. F12キー → Application タブ → Cookies → sessionid をコピー
3. 下記の session_id に貼り付け
4. 実行

期待結果:
- ステータスコード: 200 OK
- ユーザー一覧が取得できる
"""

# 管理者のセッションID（例）
session_id = "2ue7bvdnbp9wa64owo4wrwxfvo7jji2n"

headers = {
    # Cookie ヘッダーで sessionid を送信
    "Cookie": f"sessionid={session_id}"
}

# ユーザー一覧取得API を叩く
response = requests.get(
    "http://localhost:8000/api/users/",
    headers=headers
)

# ==================== レスポンス表示 ====================

print(f"ステータスコード: {response.status_code}")

if response.status_code == 200:
    # 成功時の処理
    data = response.json()
    
    # ページネーション対応
    # results キーがあればそれを使う（ページネーション有効時）
    # なければ data 全体を使う（ページネーションなし）
    users = data.get('results', data)
    
    print(f"✅ 成功！ユーザー数: {len(users)}")
    
    # 取得したユーザーの一部を表示
    print("\n取得したユーザー（最初の3件）:")
    for user in users[:3]:
        print(f"  - ID: {user['id']}, 社員番号: {user['employee_id']}, 名前: {user['username']}")

else:
    # エラー時の処理
    print(f"❌ エラー: {response.json()}")


# ==================== 実行結果の例 ====================
"""
管理者の場合:
ステータスコード: 200
✅ 成功！ユーザー数: 10

取得したユーザー（最初の3件）:
  - ID: 1, 社員番号: 9999, 名前: 管理者
  - ID: 2, 社員番号: 12345, 名前: 佐藤太郎
  - ID: 3, 社員番号: 67890, 名前: 鈴木花子


一般ユーザーの場合:
ステータスコード: 403
❌ エラー: {'detail': '管理者権限が必要です'}
"""


# ==================== ページネーションについて ====================
"""
ユーザー数10の意味:

settings.py の REST_FRAMEWORK 設定:
'PAGE_SIZE': 10  # 1ページあたり10件

views.py の UserPagination:
class UserPagination(PageNumberPagination):
    page_size = 10              # 1ページ10件
    page_size_query_param = 'page_size'
    max_page_size = 100         # 最大100件まで


つまり:
- 1ページあたり10件表示
- 今回は1ページ目の10件が返ってきた
- データベースにユーザーが10人以上いる可能性あり

全件取得する場合:
?page_size=100  # 最大100件まで一度に取得
?page=2         # 2ページ目を取得


レスポンス形式（ページネーション有効時）:
{
    "count": 100,           // 全ユーザー数
    "next": "http://localhost:8000/api/users/?page=2",
    "previous": null,
    "results": [            // 現在のページのデータ
        { "id": 1, "employee_id": "9999", ... },
        { "id": 2, "employee_id": "12345", ... },
        ...
    ]
}
"""


# ==================== その他のテスト例 ====================
"""
1. ユーザー作成テスト（管理者のみ）
response = requests.post(
    "http://localhost:8000/api/users/",
    headers=headers,
    json={
        "employee_id": "11111",
        "username": "テストユーザー",
        "password": "password123",
        "is_admin": False
    }
)

2. ユーザー詳細取得テスト
response = requests.get(
    "http://localhost:8000/api/users/1/",
    headers=headers
)

3. ユーザー更新テスト（管理者のみ）
response = requests.patch(
    "http://localhost:8000/api/users/1/",
    headers=headers,
    json={
        "username": "更新後の名前"
    }
)

4. ユーザー削除テスト（管理者のみ）
response = requests.delete(
    "http://localhost:8000/api/users/1/",
    headers=headers
)

5. 統計情報取得テスト
response = requests.get(
    "http://localhost:8000/api/users/stats/",
    headers=headers
)
"""


# ==================== セッションIDの取得方法 ====================
"""
ブラウザでセッションIDを確認する手順:

1. Chrome / Edge / Firefox を開く
2. http://localhost:8000 にアクセス
3. ログインする
4. F12キー（開発者ツールを開く）
5. 「Application」タブをクリック
6. 左側の「Cookies」を展開
7. 「http://localhost:8000」をクリック
8. 「sessionid」の値をコピー
9. このファイルの session_id に貼り付け


注意点:
- sessionid はログインごとに変わる
- ログアウトすると無効になる
- 24時間で期限切れ（settings.py の SESSION_COOKIE_AGE）
"""