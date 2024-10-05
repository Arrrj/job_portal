from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User


class UserViewSetTests(APITestCase):

    def setUp(self):
        self.url = reverse('user-register')

    def test_user_registration_success(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'roles': 'candidate',
            'password': 'testpassword123',
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_user_registration_fail(self):
        data = {
            'username': '',
            'email': 'testuser@example.com',
            'password': 'testpassword123',
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_user_registration_duplicate_email(self):
        data = {
            'username': 'testuser1',
            'email': 'testuser@example.com',
            'roles': 'candidate',
            'password': 'testpassword123',
        }
        self.client.post(self.url, data, format='json')

        data2 = {
            'username': 'testuser2',
            'email': 'testuser@example.com',  # Duplicate email
            'roles': 'candidate',
            'password': 'testpassword123',
        }
        response = self.client.post(self.url, data2, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_invalid_email(self):
        data = {
            'username': 'testuser',
            'email': 'invalid-email-format',
            'roles': 'candidate',
            'password': 'testpassword123',
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class UserLoginTests(APITestCase):
    def setUp(self):
        self.url = reverse('user-login')
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123',
            roles='candidate'
        )

    def test_login_success(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword123',
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Success')
        self.assertIn('data', response.data)
        self.assertIn('refresh', response.data['data'])
        self.assertIn('access', response.data['data'])

    def test_login_fail_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Invalid Login Credentials')

    def test_login_fail_missing_fields(self):
        data = {
            'username': 'testuser',
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)