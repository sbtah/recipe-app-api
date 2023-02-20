"""Views for Tags objects."""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from tags.models import Tag
from tags.serializers import TagSerializer


class TagViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Manage Tags in the database."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        "Retrive Tags for authenticated user."
        return self.queryset.filter(user=self.request.user).order_by("-name")
