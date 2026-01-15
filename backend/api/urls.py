from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import SubscriptionViewSet, UserViewSet, set_avatar

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipeViewSet, basename='recipe')


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/', set_avatar, name='avatar'),
    path(
        'users/subscriptions/', SubscriptionViewSet.as_view({'get': 'list'}),
        name='subscriptions'
    ),
    path(
        'users/<int:pk>/subscribe/',
        SubscriptionViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
        name='subscribe'
    ),
    path('', include(router.urls)),
]
