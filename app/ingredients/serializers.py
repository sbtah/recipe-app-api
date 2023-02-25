"""Serilizers for Ingredients APIs."""
from rest_framework import serializers
from ingredients.models import Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredients."""

    class Meta:
        model = Ingredient
        fields = ["id", "name"]
        read_only_field = ["id"]
