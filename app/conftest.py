import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def example_superuser():
    return get_user_model().objects.create_superuser(
        email="admin@example.com",
        password="testpass123!",
    )


@pytest.fixture
def example_user():
    return get_user_model().objects.create_user(
        email="user@example.com",
        password="testpass321!",
        name="Test User",
    )
