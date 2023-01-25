"""
Tests for Recipe model.
"""
import pytest
from decimal import Decimal
from recipes import models


pytestmark = pytest.mark.django_db


class TestRecipeModel:
    """Tests for Recipe objects."""

    def test_create_recipe(self, example_user):
        """Test creating a recipe is successful."""

        user = example_user

        assert models.Recipe.objects.all().count() == 0
        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample Recipe Name",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Sample Recipe Description.",
        )

        assert str(recipe) == recipe.title
        assert models.Recipe.objects.all().count() == 1
        assert isinstance(recipe, models.Recipe) is True
