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


def detail_url(ingredient_id):
    """Create and return an ingredient detail url."""
    return reverse("recipes:ingredient-detail", args=[ingredient_id])


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

    def test_update_ingredient(
        self,
        authenticated_client,
        create_example_ingredient,
    ):
        """Test updating and Ingredient."""

        ingredient = create_example_ingredient
        payload = {"name": "New Name!"}
        url = detail_url(ingredient_id=ingredient.id)
        res = authenticated_client.patch(url, payload)
        ingredient.refresh_from_db()

        assert res.status_code == status.HTTP_200_OK
        assert ingredient.name == payload["name"]

    def test_delete_ingredient(
        self,
        authenticated_client,
        create_example_ingredient,
    ):
        """Test deleting and Ingredient."""

        ingredient = create_example_ingredient
        url = detail_url(ingredient_id=ingredient.id)
        assert Ingredient.objects.count() == 1
        res = authenticated_client.delete(url)

        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert Ingredient.objects.count() == 0

    def test_filter_ingredients_assigned_to_recipes(
        self,
        authenticated_client,
        create_example_recipe,
        create_example_ingredients_list,
    ):
        """Test listing Ingredients by those assigned to Recipes."""

        recipe = create_example_recipe
        ingredients = create_example_ingredients_list
        recipe.ingredients.add(ingredients[0])
        serializer_1 = IngredientSerializer(ingredients[0])
        res = authenticated_client.get(INGREDIENTS_URL, {"assigned_only": 1})

        assert serializer_1.data in res.data
        assert len(res.data) == 1

    def test_filtered_ingredients_unique(
        self,
        authenticated_client,
        create_example_recipe,
        create_example_recipe_2,
        create_example_ingredients_list,
    ):
        """Test filtered Ingredients returns unique list."""

        ingredients = create_example_ingredients_list
        recipe_1 = create_example_recipe
        recipe_2 = create_example_recipe_2
        recipe_1.ingredients.add(ingredients[0])
        recipe_2.ingredients.add(ingredients[0])
        res = authenticated_client.get(INGREDIENTS_URL, {"assigned_only": 1})

        assert len(res.data) == 1
