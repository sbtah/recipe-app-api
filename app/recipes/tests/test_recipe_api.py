"""
Tests for recipe APIs.
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe
from recipes.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPES_URL = reverse('recipes:recipe-list')


def detail_url(recipe_id):
    """Create and return recipe detail URL."""
    return reverse('recipes:recipe-detail', args=[recipe_id])


def create_recipe(user, **kwargs):
    """Create and return sample recipe."""

    default = {
        'title': 'Sample Recipe',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample Description',
        'link': 'http://example.com/recipe.pdf',
    }
    default.update(kwargs)
    recipe = Recipe.objects.create(
        user=user,
        **default,
       )

    return recipe


def create_user(**kwargs):
    """Create and return a new user."""

    return get_user_model().objects.create_user(**kwargs)


class PublicRecipeAPITests(TestCase):
    """Test Unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to call API."""

        response = self.client.get(RECIPES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='samplepass123',
            name='Test Name',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving list of reipces."""

        create_recipe(user=self.user)
        create_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""

        other_user = create_user(
            email='other@example.com',
            password='otherpass123',
            name='Other Name',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)
        response = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""

        recipe = create_recipe(user=self.user)
        url = detail_url(recipe_id=recipe.id)
        response = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""

        payload = {
            'title': 'Sample Recipe',
            'time_minutes': 22,
            'price': Decimal('5.25'),
        }
        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of a recipe."""

        original_url = 'https://example.com/recipe.pdf/'
        recipe = create_recipe(
            user=self.user,
            title='Sample Recipe 2',
            link=original_url,
        )
        payload = {
            'link': 'https://example.com/new-recipe.pdf/'
        }
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.link, payload['link'])
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(recipe.title, 'Sample Recipe 2')

    def test_full_update(self):
        """Test full update of a recipe."""

        recipe = create_recipe(
            user=self.user,
            title='Sample Recipe Title',
            link='https://example.com/recipe.pdf/',
            description='Sample Recipe Description.'
        )
        payload = {
            'title': 'New Title',
            'link': 'https://example.com/new-recipe.pdf/',
            'description': 'New Recipe Descritpion',
            'time_minutes': 10,
            'price': Decimal('2.55'),
        }
        url = detail_url(recipe.id)
        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

    def test_update_user_returns_error(self):
        """Test updating recipe's user returns an error."""

        new_user = create_user(
            email='nextuser@example.com',
            password='testpass000',
        )
        recipe = create_recipe(user=self.user)
        payload = {
            'user': new_user.id
        }
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(response.status_code , status.HTTP_200_OK)

    def test_delete_recipe(self):
        """Test deleting a recipe successful."""

        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        self.assertEqual(Recipe.objects.all().count(), 1)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Recipe.objects.all().count(), 0)

    def test_delete_recipe_other_users_returns_error(self):
        """Test trying to delete another user's recipe gives error."""

        new_user = create_user(
            email='user2@example.com',
            password='test123!',
            )
        recipe = create_recipe(user=new_user)
        url = detail_url(recipe.id)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
