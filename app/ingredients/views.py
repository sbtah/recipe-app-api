"""Views for Ingredients objects."""
from ingredients.models import Ingredient
from ingredients.serializers import IngredientSerializer
from recipes.views import BaseRecipeAttrViewSet


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage Ingredients in the database."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
