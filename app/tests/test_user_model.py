"""
Tests for user model.
"""
import pytest
from django.contrib.auth import get_user_model


pytestmark = pytest.mark.django_db


class TestUserModel:
    """Test cases related to user model."""

    def test_create_user_with_email_successful(self):
        """Test creating user with email is successful."""

        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        assert user.email == email
        assert user.check_password(password) is True

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""

        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            assert user.email == expected

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""

        with pytest.raises(ValueError):
            get_user_model().objects.create_user("", "samplepass123")

    def test_create_superuser(self):
        """Test creating a superuser."""

        superuser = get_user_model().objects.create_superuser(
            email="test@example.com",
            password="samplepass123",
        )

        assert superuser.is_superuser is True
        assert superuser.is_staff is True
