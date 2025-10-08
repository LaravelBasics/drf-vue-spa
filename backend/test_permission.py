# test_permission.py
# 一般ユーザー版
# import requests

# # 一般ユーザーのトークン（ログインしてアプリケーションタブのcookieにあるsessionid）
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

# 期待結果: 403 Forbidden
# Desktop\template\backend> python test_permission.py
# ステータスコード: 403
# レスポンス: {'detail': '管理者権限が必要です'}

# test_permission.py（管理者版）
import requests

# 管理者のトークン
session_id = "2ue7bvdnbp9wa64owo4wrwxfvo7jji2n"

headers = {
    "Cookie": f"sessionid={session_id}"
}

# ユーザー一覧取得を試みる
response = requests.get(
    "http://localhost:8000/api/users/",
    headers=headers
)

print(f"ステータスコード: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ 成功！ユーザー数: {len(data.get('results', data))}")
else:
    print(f"レスポンス: {response.json()}")

# 期待結果: 200 OK
#  python test_permission.py
# ステータスコード: 200
# ✅ 成功！ユーザー数: 10
# ユーザー数10の意味 📊
# python# ページネーション設定
# class UserPagination(PageNumberPagination):
#     page_size = 10  # ← これ！
#     page_size_query_param = 'page_size'
#     max_page_size = 10
# つまり:

# 1ページあたり10件表示
# 今回は1ページ目の10件が返ってきた
# DBにユーザーが10人以上いる可能性あり