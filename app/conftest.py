from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from recipes.models import Recipe


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


@pytest.fixture
def create_example_recipe(example_user):
    """Create and return sample Recipe."""

    return Recipe.objects.create(
        user=example_user,
        title="Sample Recipe Name",
        time_minutes=5,
        price=Decimal("5.50"),
        description="Sample Recipe Description.",
    )


@pytest.fixture
def authenticated_client(example_user, api_client):
    user = example_user
    api_client.force_authenticate(user=user)
    yield api_client
    api_client.force_authenticate(user=None)


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()
