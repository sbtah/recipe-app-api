"""
Tests for Ingredient API.
"""
import pytest
from django.urls import reverse
from ingredients.models import Ingredient
from ingredients.serializers import IngredientSerializer
from rest_framework import status


INGREDIENTS_URL = reverse("recipes:ingredient-list")
pytestmark = pytest.mark.django_db


class TestPublicIngredientApi:
    """Test unauthenticated API requests."""

    def test_authentication_required(self, api_client):
        """Test that authentication is required for retrieving Ingredients."""

        res = api_client.get(INGREDIENTS_URL)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestPrivateIngredientApi:
    """Test authenticated API requests."""

    def test_retrive_ingredients(
        self,
        authenticated_client,
        create_example_ingredients_list,
    ):
        """Test retrieving a list of Ingredients."""

        create_example_ingredients_list
        res = authenticated_client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_retrive_ingredients_limited_to_user(
        self,
        authenticated_client,
        create_example_ingredients_list,
        create_example_ingredient_for_user_2,
    ):
        """Test list of Ingredients is limited to authenticated user."""

        create_example_ingredients_list
        create_example_ingredient_for_user_2
        res = authenticated_client.get(INGREDIENTS_URL)

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 3
