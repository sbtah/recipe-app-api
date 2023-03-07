"""
Test for the health check API.
"""
from django.urls import reverse
from rest_framework import status


class TestHealthCheckApi:
    """Test the health check API."""

    def test_health_check(self, api_client):
        """Test health check API endpoint."""

        url = reverse("health-check")
        res = api_client.get(url)

        assert res.status_code == status.HTTP_200_OK
