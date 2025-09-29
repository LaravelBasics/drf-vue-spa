from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()

class UserModelTest(TestCase):
    """ユーザーモデルのテスト"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'employee_id': 1001,
            'password': 'testpass123'
        }
    
    def test_create_user(self):
        """ユーザー作成テスト"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.employee_id, 1001)
        self.assertFalse(user.is_admin)
    
    def test_create_admin_user(self):
        """管理者ユーザー作成テスト"""
        admin_data = {**self.user_data, 'is_admin': True}
        user = User.objects.create_user(**admin_data)
        self.assertTrue(user.is_admin)

class UserAPITest(APITestCase):
    """ユーザーAPI のテスト"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            employee_id=1000,
            password='adminpass',
            is_admin=True
        )
        self.regular_user = User.objects.create_user(
            username='user',
            employee_id=1001,
            password='userpass',
            is_admin=False
        )
        self.client.force_authenticate(user=self.admin_user)
    
    def test_list_users(self):
        """ユーザー一覧取得テスト"""
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_create_user(self):
        """ユーザー作成テスト"""
        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'employee_id': 1002,
            'is_admin': False,
            'password': 'newpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_delete_last_admin_fails(self):
        """最後の管理者削除失敗テスト"""
        # 他の管理者を削除して1人にする
        url = reverse('user-detail', args=[self.admin_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_search_users(self):
        """ユーザー検索テスト"""
        url = reverse('user-list')
        response = self.client.get(url, {'search': 'admin'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)