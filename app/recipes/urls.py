"""
URL mappings for the recipes API.
"""
from django.urls import path, include
from recipes import views
from rest_framework.routers import DefaultRouter


app_name = "recipes"


router = DefaultRouter()
router.register("recipes", views.RecipeViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
