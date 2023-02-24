"""
Tests for Ingredient model.
"""
import pytest
from ingredients import models


pytestmark = pytest.mark.django_db


class TestIngredientModel:
    """Tests for Ingredient objects."""

    def test_create_ingredient(self, example_user):
        """Test creating a Ingredient object is successful."""

        assert models.Ingredient.objects.count() == 0
        user = example_user
        ingredient = models.Ingredient.objects.create(
            user=user,
            name="Ingredient1",
        )

        assert models.Ingredient.objects.count() == 1
        assert isinstance(ingredient, models.Ingredient) is True
        assert str(ingredient) == ingredient.name
