from django_filters import CharFilter, FilterSet, NumberFilter

from recipes.models import Ingredient, Recipe


class RecipeFilter(FilterSet):
    """
    Класс-фильтр для рецептов. Предоставляет фильтрацию по автору,
    тегам, а также по нахождению рецептов в избранном и списке покупок.
    """

    tags = CharFilter(method='filter_tags')
    author = NumberFilter(field_name='author__id')
    is_favorited = NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = NumberFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filter_tags(self, queryset, name, data):
        tags = self.request.query_params.getlist('tags')

        if not tags:
            return queryset

        queryset = queryset.filter(tags__slug__in=tags).distinct()
        return queryset

    def _filter_by_user_relation(self, queryset, data, related_field):
        """
        Фильтр для проверки наличия/отсутствия связи
        между рецептом и пользователем.
        """

        user = self.request.user
        if not user.is_authenticated:
            return queryset

        if data:
            return queryset.filter(**{related_field: user})
        return queryset.exclude(**{related_field: user})

    def filter_is_favorited(self, queryset, name, data):
        return self._filter_by_user_relation(
            queryset, data, 'favorite_set__user'
        )

    def filter_is_in_shopping_cart(self, queryset, name, data):
        return self._filter_by_user_relation(
            queryset, data, 'shoppingcart_set__user'
        )


class IngredientFilter(FilterSet):
    """
    Класс-фильтр для ингредиентов. Предоставляет поиск по частичному
    вхождению в начале названия ингредиента.
    """

    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
