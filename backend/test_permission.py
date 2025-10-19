"""
権限テストスクリプト

Usage:
    1. ブラウザでログイン
    2. F12 → Application → Cookies → sessionid をコピー
    3. SESSION_ID を更新して実行

Requirements:
    pip install requests
"""

import requests

# ==================== 設定 ====================

BASE_URL = "http://localhost:8000"
SESSION_ID = "your-session-id-here"  # ← ブラウザからコピーして貼り付け

headers = {"Cookie": f"sessionid={SESSION_ID}"}

# ==================== テスト実行 ====================


def test_user_list():
    """ユーザー一覧取得テスト"""
    response = requests.get(f"{BASE_URL}/api/users/", headers=headers)

    print(f"ステータスコード: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        users = data.get("results", data)

        print(f"✅ 成功！ユーザー数: {len(users)}")
        print("\n取得したユーザー（最初の3件）:")
        for user in users[:3]:
            print(
                f"  - ID: {user['id']}, 社員番号: {user['employee_id']}, 名前: {user['username']}"
            )
    else:
        print(f"❌ エラー: {response.json()}")


def test_user_create():
    """ユーザー作成テスト（管理者のみ）"""
    response = requests.post(
        f"{BASE_URL}/api/users/",
        headers=headers,
        json={
            "employee_id": "99999",
            "username": "テストユーザー",
            "password": "test1234",
            "email": "test@example.com",
            "is_admin": False,
        },
    )

    print(f"\nユーザー作成: {response.status_code}")
    print(response.json())


def test_user_stats():
    """統計情報テスト"""
    response = requests.get(f"{BASE_URL}/api/users/stats/", headers=headers)

    print(f"\n統計情報: {response.status_code}")
    if response.status_code == 200:
        print(response.json())


if __name__ == "__main__":
    print("=" * 50)
    print("権限テスト開始")
    print("=" * 50)

    test_user_list()
    # test_user_create()  # 必要に応じてコメント解除
    # test_user_stats()   # 必要に応じてコメント解除

    print("\n" + "=" * 50)
    print("テスト終了")
    print("=" * 50)
