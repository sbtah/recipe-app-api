"""Serilizers for tags APIs."""
from rest_framework import serializers
from tags.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tags."""

    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]
