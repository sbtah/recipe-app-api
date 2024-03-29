"""
Tests for the Tags API.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from tags.models import Tag
from tags.serializers import TagSerializer

TAGS_URL = reverse("recipes:tag-list")
pytestmark = pytest.mark.django_db


def detail_url(tag_id):
    return reverse("recipes:tag-detail", args=[tag_id])


class TestPublicTagsApi:
    """Test unauthenticated API requests."""

    def test_authentication_required(self, api_client):
        """Test that authentication is required to access API."""

        res = api_client.get(TAGS_URL)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestPrivateTagsApi:
    """
    Test authenticated API requests.
    """

    def test_retrive_tags(
        self, create_example_tag_1, create_example_tag_2, authenticated_client
    ):
        """Test retrieving a list of Tags."""

        create_example_tag_1
        create_example_tag_2
        res = authenticated_client.get(TAGS_URL)
        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_tags_limited_to_user(
        self,
        authenticated_client,
        example_user,
        create_example_tag_1,
        create_example_tag_2,
        create_example_tag_for_user_2,
    ):
        """Test list of Tags is limited to authenticated user."""

        create_example_tag_1
        create_example_tag_2
        create_example_tag_for_user_2
        res = authenticated_client.get(TAGS_URL)
        tags = Tag.objects.filter(user=example_user).order_by("-name")
        serializer = TagSerializer(tags, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 2
        assert res.data == serializer.data
        assert Tag.objects.all().count() == 3

    def test_update_tag(self, authenticated_client, create_example_tag_1):
        """Test updating a Tag is successful."""

        tag = create_example_tag_1
        payload = {"name": "Dessert"}
        url = detail_url(tag.id)
        res = authenticated_client.patch(url, payload)

        assert res.status_code == status.HTTP_200_OK
        tag.refresh_from_db()
        assert tag.name == payload["name"]

    def test_delete_tag(self, authenticated_client, create_example_tag_1):
        """Test deleting a Tag is successful."""

        tag = create_example_tag_1
        url = detail_url(tag.id)
        res = authenticated_client.delete(url)

        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert Tag.objects.all().count() == 0

    def test_filter_tags_assigned_to_recipes(
        self,
        authenticated_client,
        create_example_tag_1,
        create_example_tag_2,
        create_example_recipe,
    ):
        """Test listing Tags to those assigned to Recipes."""

        tag_1 = create_example_tag_1
        tag_2 = create_example_tag_2
        recipe_1 = create_example_recipe
        recipe_1.tags.add(tag_1)
        serializer_1 = TagSerializer(tag_1)
        serializer_2 = TagSerializer(tag_2)
        res = authenticated_client.get(TAGS_URL, {"assigned_only": 1})

        assert serializer_1.data in res.data
        assert serializer_2.data not in res.data
        assert len(res.data) == 1

    def test_filtered_tags_unique(
        self,
        authenticated_client,
        create_example_tag_1,
        create_example_tag_2,
        create_example_recipe,
        create_example_recipe_2,
    ):
        """Test filtered tags returns a unique list."""

        tag_1 = create_example_tag_1
        create_example_tag_2
        recipe_1 = create_example_recipe
        recipe_2 = create_example_recipe_2
        recipe_1.tags.add(tag_1)
        recipe_2.tags.add(tag_1)
        res = authenticated_client.get(TAGS_URL, {"assigned_only": 1})

        assert len(res.data) == 1
