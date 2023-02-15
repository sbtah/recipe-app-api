"""
Tests for recipe APIs.
"""
from decimal import Decimal

import pytest
from django.urls import reverse
from recipes.models import Recipe
from recipes.serializers import RecipeDetailSerializer, RecipeSerializer
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

    def test_create_recipe(self, authenticated_client, example_user):
        """Test creating a recipe."""

        payload = {
            "title": "Sample test recipe",
            "time_minutes": 30,
            "price": Decimal("5.99"),
        }
        res = authenticated_client.post(RECIPES_URL, payload)

        assert res.status_code == status.HTTP_201_CREATED
        recipe = Recipe.objects.get(id=res.data["id"])
        for k, v in payload.items():
            assert getattr(recipe, k) == v
        assert recipe.user == example_user

    def test_perform_partial_update(
        self,
        authenticated_client,
        create_example_recipe,
        example_user,
    ):
        """Test partial update on recipe."""

        user = example_user
        recipe = create_example_recipe
        payload = {"title": "New recipe title"}
        url = detail_url(recipe_id=recipe.id)
        res = authenticated_client.patch(url, payload)

        assert res.status_code == status.HTTP_200_OK
        recipe.refresh_from_db()
        assert recipe.title == payload["title"]
        assert recipe.user == user

    def test_perform_full_update(
        self, authenticated_client, create_example_recipe, example_user
    ):
        """Test full update of recipe."""

        user = example_user
        recipe = create_example_recipe
        payload = {
            "title": "New recipe title",
            "time_minutes": 12,
            "price": Decimal("7.70"),
            "description": "New description",
            "link": "http://example.com/new-recipe.pdf/",
        }
        url = detail_url(recipe_id=recipe.id)
        res = authenticated_client.put(url, payload)

        assert res.status_code == status.HTTP_200_OK
        recipe.refresh_from_db()
        for k, v in payload.items():
            assert getattr(recipe, k) == v
        assert recipe.user == user

    def test_update_user_returns_error(
        self,
        authenticated_client,
        create_example_recipe,
        example_user,
        example_user_2,
    ):
        """Test changing recipe's user results in an error."""

        recipe = create_example_recipe
        new_user = example_user_2
        user = example_user
        payload = {"user": new_user.id}
        url = detail_url(recipe_id=recipe.id)
        res = authenticated_client.patch(url, payload)
        recipe.refresh_from_db()

        assert res.status_code == status.HTTP_200_OK
        assert recipe.user == user

    def test_delete_recipe(
        self,
        authenticated_client,
        create_example_recipe,
    ):
        """Test deleting recipe successful."""

        recipe = create_example_recipe
        url = detail_url(recipe_id=recipe.id)
        res = authenticated_client.delete(url)

        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert Recipe.objects.filter(id=recipe.id).exists() is False

    def test_delete_other_users_recipe_error(
        self,
        authenticated_client,
        create_example_recipe_for_user_2,
    ):
        """Test trying to delete another users recipe returns an error."""

        recipe = create_example_recipe_for_user_2
        url = detail_url(recipe_id=recipe.id)
        res = authenticated_client.delete(url)

        assert res.status_code == status.HTTP_404_NOT_FOUND
        assert Recipe.objects.filter(id=recipe.id).exists() is True
