"""
Test for the Django admin modifications.
"""
import pytest
from django.urls import reverse


pytestmark = pytest.mark.django_db


class TestAdminSite:
    """Tests for Django Admin."""

    def test_users_list(self, client, example_superuser, example_user):
        """Test that users are listed on Admin page."""

        user = example_user
        client.force_login(example_superuser)

        url = reverse("admin:users_user_changelist")
        res = client.get(url)

        assert user.name in str(res.content)
        assert user.email in str(res.content)

    def test_edit_user_page(self, client, example_superuser, example_user):
        """Test the edit user page works."""

        user = example_user
        client.force_login(example_superuser)

        url = reverse("admin:users_user_change", args=[user.id])
        res = client.get(url)

        assert res.status_code == 200

    def test_create_user_page(self, client, example_superuser, example_user):
        """Test the create user page works."""

        client.force_login(example_superuser)

        url = reverse("admin:users_user_add")
        res = client.get(url)

        assert res.status_code == 200
