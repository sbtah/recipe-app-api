"""
Tests for recipe APIs.
"""
from decimal import Decimal

import pytest
from django.urls import reverse
from recipes.models import Recipe
from tags.models import Tag
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

    def test_create_recipe_with_new_tags(
        self,
        authenticated_client,
        example_user,
    ):
        """Test creating a recipe with new Tags."""

        user = example_user
        payload = {
            "title": "Sample test recipe",
            "time_minutes": 30,
            "price": Decimal("5.99"),
            "tags": [{"name": "Tag1"}, {"name": "Tag2"}],
        }
        res = authenticated_client.post(RECIPES_URL, payload, format="json")

        assert res.status_code == status.HTTP_201_CREATED
        assert Recipe.objects.all().count() == 1
        assert Tag.objects.all().count() == 2
        recipes = Recipe.objects.filter(user=user)
        assert recipes[0].tags.count() == 2
        for tag in payload["tags"]:
            exists = (
                recipes[0]
                .tags.filter(
                    name=tag["name"],
                    user=user,
                )
                .exists()
            )
            assert exists is True

    def test_create_recipe_with_existing_tags(
        self,
        authenticated_client,
        example_user,
        create_example_tag_1,
    ):
        """Test creating a recipe with existing Tag."""

        tag_1 = create_example_tag_1
        user = example_user
        payload = {
            "title": "New recipe title",
            "time_minutes": 12,
            "price": Decimal("7.70"),
            "tags": [{"name": tag_1.name}, {"name": "Tag New"}],
            "description": "New description",
            "link": "http://example.com/new-recipe.pdf/",
        }
        res = authenticated_client.post(RECIPES_URL, payload, format="json")

        assert res.status_code == status.HTTP_201_CREATED
        assert Recipe.objects.all().count() == 1
        assert Tag.objects.all().count() == 2
        recipes = Recipe.objects.filter(user=user)
        assert recipes[0].tags.count() == 2
        assert tag_1 in recipes[0].tags.all()
        for tag in payload["tags"]:
            exists = (
                recipes[0]
                .tags.filter(
                    name=tag["name"],
                    user=user,
                )
                .exists()
            )
            assert exists is True

    def test_create_tag_on_update(
        self,
        authenticated_client,
        create_example_recipe,
        example_user,
    ):
        """Test creating a Tag when updating a Recipe."""

        recipe = create_example_recipe
        user = example_user
        payload = {"tags": [{"name": "Other"}]}
        url = detail_url(recipe_id=recipe.id)
        res = authenticated_client.patch(url, payload, format="json")

        assert res.status_code == status.HTTP_200_OK
        new_tag = Tag.objects.get(user=user, name="Other")
        assert new_tag in recipe.tags.all()

    def test_update_recipe_assign_tag(
        self,
        authenticated_client,
        create_example_recipe,
        create_example_tag_1,
        create_example_tag_2,
    ):
        """Test assigning an existing Tag when updating a recipe."""

        tag_1 = create_example_tag_1
        tag_2 = create_example_tag_2
        recipe = create_example_recipe
        recipe.tags.add(tag_1)
        payload = {"tags": [{"name": f"{tag_2.name}"}]}
        url = detail_url(recipe_id=recipe.id)
        res = authenticated_client.patch(url, payload, format="json")

        assert res.status_code == status.HTTP_200_OK
        assert tag_2 in recipe.tags.all()
        assert tag_1 not in recipe.tags.all()

    def test_clear_recipe_tags(
        self,
        authenticated_client,
        create_example_recipe,
        create_example_tag_1,
        create_example_tag_2,
    ):
        """Test clearing a Recipe Tags."""

        recipe = create_example_recipe
        tag_1 = create_example_tag_1
        tag_2 = create_example_tag_2
        recipe.tags.add(tag_1, tag_2)
        payload = {"tags": []}
        url = detail_url(recipe_id=recipe.id)
        res = authenticated_client.patch(url, payload, format="json")

        assert res.status_code == status.HTTP_200_OK
        assert recipe.tags.count() == 0
