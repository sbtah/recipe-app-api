"""
Tests for Tag model.
"""
import pytest
from tags import models


pytestmark = pytest.mark.django_db


class TestTagModel:
    """Tests for Tag objects."""

    def test_create_tag(self, example_user):
        """Test creating Tag object is successful."""

        user = example_user

        assert models.Tag.objects.all().count() == 0
        tag = models.Tag.objects.create(user=user, name="Tag1")

        assert models.Tag.objects.all().count() == 1
        assert str(tag) == tag.name
        assert isinstance(tag, models.Tag) is True
