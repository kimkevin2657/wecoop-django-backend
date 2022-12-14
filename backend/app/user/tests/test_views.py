import json

from rest_framework import status
from rest_framework.test import APITestCase

from app.user.models import User, Device


class UserLoginViewTest(APITestCase):
    view_path = "/v1/user/login/"

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(email="test@test.com", password="test123!")

    def test_login_success_response(self):
        response = self.client.post(self.view_path, {"email": "test@test.com", "password": "test123!"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertListEqual(sorted(list(response.data)), sorted(["access", "refresh"]))  # 데이터 확인 어려워 키만 확인

    def test_login_failure_response_from_invalid_email(self):
        response = self.client.post(self.view_path, {"email": "test2@test.com", "password": "test123!"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"nonFieldErrors": ["인증정보가 일치하지 않습니다."]})

    def test_login_failure_response_from_invalid_password(self):
        response = self.client.post(self.view_path, {"email": "test@test.com", "password": "test123!!"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"nonFieldErrors": ["인증정보가 일치하지 않습니다."]})


class UserLogoutViewTest(APITestCase):
    view_path = "/v1/user/logout/"

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(email="test@test.com", password="test123!")
        Device.objects.create(user=user, uid="uid", token="token")

    def setUp(self) -> None:
        self.user = User.objects.get(email="test@test.com")
        self.client.force_authenticate(self.user)

    def test_logout_success_response(self):
        response = self.client.post(self.view_path)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {})

    def test_logout_success_response_together_uid(self):
        response = self.client.post(self.view_path, {"uid": "uid"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(self.user.device_set.filter(uid="uid").exists())
        self.assertEqual(response.data, {})


class UserRefreshViewTest(APITestCase):
    view_path = "/v1/user/refresh/"

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(email="test@test.com", password="test123!")

    def setUp(self) -> None:
        user = User.objects.get(email="test@test.com")
        self.client.force_authenticate(user)

    def test_refresh_success_response(self):
        response = self.client
