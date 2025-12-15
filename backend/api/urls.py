from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserCreateView
from .views import IngredientViewSet, RecipeViewSet, UserViewSet

router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/', UserCreateView.as_view(), name='user-create'),
    path('recipes/<int:pk>/get-link/',
         RecipeViewSet.as_view({'get': 'get_link'}), name='recipe-get-link'),
]
