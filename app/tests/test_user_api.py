"""
Tests for the user API.
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status


pytestmark = pytest.mark.django_db


CREATE_USER_URL = reverse("users:create")
TOKEN_URL = reverse("users:token")
ME_URL = reverse("users:me")


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class TestUserPublicAPI:
    """Test the the public features of the user API."""

    def test_create_user_success(self, api_client):
        """Test creating a user is successfull."""

        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name",
        }

        assert get_user_model().objects.all().count() == 0
        res = api_client.post(CREATE_USER_URL, payload)
        assert res.status_code == status.HTTP_201_CREATED
        assert get_user_model().objects.all().count() == 1
        user = get_user_model().objects.get(email=payload["email"])
        assert user.check_password(payload["password"]) is True
        assert "password" not in res.data

    def test_user_with_email_exists_error(self, api_client):
        """Test error is returned if user with email already exists."""

        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name",
        }
        create_user(**payload)
        res = api_client.post(CREATE_USER_URL, payload)
        assert get_user_model().objects.all().count() == 1
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert get_user_model().objects.all().count() == 1

    def test_password_too_short_error(self, api_client):
        """Test an error is returned if password less then 5 characters."""

        payload = {
            "email": "test@example.com",
            "password": "test",
            "name": "Test Name",
        }
        res = api_client.post(CREATE_USER_URL, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        user_exists = (
            get_user_model()
            .objects.filter(
                email=payload["email"],
            )
            .exists()
        )
        assert user_exists is False
        assert get_user_model().objects.all().count() == 0

    def test_creating_token_for_user(self, api_client):
        """Test generates token for valid credentials."""

        user_details = {
            "name": "Test Name",
            "email": "test@example.com",
            "password": "testpass123!",
        }
        create_user(**user_details)
        payload = {
            "email": user_details["email"],
            "password": user_details["password"],
        }
        res = api_client.post(TOKEN_URL, payload)
        assert "token" in res.data
        assert res.status_code == status.HTTP_200_OK

    def test_create_token_bad_credentials(self, api_client, example_user):
        """Test returns error if credentials invalid."""

        user = example_user
        payload = {
            "email": user.email,
            "password": "badpass",
        }
        res = api_client.post(TOKEN_URL, payload)

        assert "token" not in res.data
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_token_blank_password(self, api_client):
        """Test posting a blank password returns an error."""

        payload = {
            "email": "test@example.com",
            "password": "",
        }
        res = api_client.post(TOKEN_URL, payload)

        assert "token" not in res.data
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_user_unauthorized(self, api_client):
        """Test authentication is required for users."""

        res = api_client.get(ME_URL)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserPrivateAPI:
    """Test API requests that require authentication."""

    def test_retrieve_profile_success(self, authenticated_client):
        """Test retrieving profile for logged user."""

        res = authenticated_client.get(ME_URL)

        assert res.status_code == status.HTTP_200_OK
        # TODO:
        # FIX this....
        assert res.data == {"name": "Test User", "email": "user@example.com"}

    def test_post_me_not_allowed(self, authenticated_client):
        """Test POST is not allowed for the me endpoint."""

        res = authenticated_client.post(ME_URL)

        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_update_user_profile(self, example_user, authenticated_client):
        """Test updating the user profile, for the authenticated user."""

        user = example_user
        payload = {"name": "New Name", "password": "newpass123!"}
        res = authenticated_client.patch(ME_URL, payload)
        user.refresh_from_db()

        assert user.name == payload["name"]
        assert user.check_password(payload["password"]) is True
        assert res.status_code == status.HTTP_200_OK
