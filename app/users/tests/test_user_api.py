"""
Tests for the users API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('users:create')
TOKEN_URL = reverse('users:token')


def create_user(**kwargs):
    """Create and return new User."""

    return get_user_model().objects.create_user(**kwargs)


class PubklicUserAPITests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a User successful"""

        payload = {
            'email': 'test@example.com',
            'password': 'testpass123!',
            'name': 'TestName',
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_with_email_exists_error(self):
        """Test that error is raised is user with email exists."""

        payload = {
            'email': 'test@example.com',
            'password': 'testpass321111',
            'name': 'TestName',
        }
        create_user(**payload)
        resposne = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(resposne.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""

        payload = {
            'email': 'test@example.com',
            'password': 'as1',
            'name': 'TestName',
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email'],
            ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generate token for valid credentials."""

        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'samplepass123'
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials are invalid."""

        create_user(
            email='test@example.com',
            password='samplepass123',
        )
        payload = {
            'email': 'test@example.com',
            'password': 'wrongpass123',
        }
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""

        payload = {
            'email': 'test@example.com',
            'password': '',
        }
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
