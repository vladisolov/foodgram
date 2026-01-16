from django.conf import settings
from django.db.models import Prefetch, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer, RecipeMinifiedSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, TagSerializer
)
from .utils import generate_shopping_list_pdf


def redirect_from_short_link(request, token):
    """Редирект с короткой ссылки на страницу рецепта."""

    recipe = get_object_or_404(Recipe, short_link_token=token)
    return redirect(f'{settings.HOST_NAME}/recipes/{recipe.id}/')


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.select_related('author').prefetch_related(
        Prefetch(
            'recipe_ingredients',
            queryset=RecipeIngredient.objects.select_related('ingredient')
        ), 'tags'
    )
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def _handle_recipe_relation(self, request, pk, model, action_name):
        """Обработчик для операций с рецептами (избранное, список покупок)."""

        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if model.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                raise ValidationError(f'Рецепт уже добавлен в {action_name}.')

            model.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            relation = model.objects.filter(
                user=request.user, recipe=recipe
            ).first()

            if not relation:
                raise ValidationError(f'Рецепта нет в {action_name}.')

            relation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('GET',), detail=True, url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return Response({'short-link': recipe.short_link})

    @action(
        methods=('POST', 'DELETE'), detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранное."""

        return self._handle_recipe_relation(
            request, pk, Favorite, 'избранное'
        )

    @action(
        methods=('POST', 'DELETE'), detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта в список покупок."""

        return self._handle_recipe_relation(
            request, pk, ShoppingCart, 'список покупок'
        )

    @action(
        methods=('GET',), detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок в формате PDF."""

        shopping_cart = ShoppingCart.objects.filter(
            user=request.user
        ).select_related('recipe')

        if not shopping_cart.exists():
            raise ValidationError('Список покупок пуст.')

        recipes = [item.recipe for item in shopping_cart]

        ingredients = (
            RecipeIngredient.objects.filter(recipe__in=recipes)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        pdf = generate_shopping_list_pdf(ingredients)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.pdf"'
        )
        return response
