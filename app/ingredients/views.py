"""Views for Ingredients objects."""
from ingredients.models import Ingredient
from ingredients.serializers import IngredientSerializer
from rest_framework import mixins, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class IngredientViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Manage Ingredients in the database."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        "Retrive Ingredients for authenticated user."
        return self.queryset.filter(user=self.request.user).order_by("-name")
