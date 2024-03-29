"""
URL mappings for the recipes API.
"""
from django.urls import include, path
from recipes.views import RecipeViewSet
from rest_framework.routers import DefaultRouter
from tags.views import TagViewSet
from ingredients.views import IngredientViewSet


app_name = "recipes"


router = DefaultRouter()
router.register("recipes", RecipeViewSet)
router.register("tags", TagViewSet)
router.register("ingredients", IngredientViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
