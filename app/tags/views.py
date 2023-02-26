"""Views for Tags objects."""
from recipes.views import BaseRecipeAttrViewSet
from tags.models import Tag
from tags.serializers import TagSerializer


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage Tags in the database."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
