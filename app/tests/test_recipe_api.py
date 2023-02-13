"""
Tests for recipe APIs.
"""
import pytest
from django.urls import reverse
from recipes.models import Recipe
from recipes.serializers import RecipeSerializer, RecipeDetailSerializer
from rest_framework import status


RECIPES_URL = reverse("recipes:recipe-list")
pytestmark = pytest.mark.django_db


def detail_url(recipe_id):
    """Create and return recipe detail URL."""
    return reverse("recipes:recipe-detail", args=[recipe_id])


class TestPublicRecipeApi:
    """
    Test unauthenticated API requests.
    """

    def test_authentication_required(self, api_client):
        """Test that authentication is required to access API."""

        res = api_client.get(RECIPES_URL)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestPrivateRecipeApi:
    """
    Test authenticated API requests.
    """

    def test_retrive_recipes(
        self,
        create_example_recipe,
        authenticated_client,
    ):
        """Test retrieving a list of recipes."""

        # recipe_1 = create_example_recipe
        # recipe_2 = create_example_recipe
        for _ in range(3):
            create_example_recipe
        res = authenticated_client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_retrive_recipes_limited_to_user(
        self,
        example_user,
        create_example_recipe,
        create_example_recipe_for_user_2,
        authenticated_client,
    ):
        """Test list of recipes is limited to authenticated user."""

        user = example_user
        for _ in range(3):
            create_example_recipe
            create_example_recipe_for_user_2
        res = authenticated_client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=user)
        serializer = RecipeSerializer(recipes, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_get_recipe_detail(
        self,
        create_example_recipe,
        authenticated_client,
    ):
        """Test get recipe detail."""

        recipe = create_example_recipe
        url = detail_url(recipe_id=recipe.id)
        res = authenticated_client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data
