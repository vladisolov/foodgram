from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.crypto import get_random_string

from .constants import (
    INGREDIENT_MAX_LENGTH, MEASUREMENT_UNIT_MAX_LENGTH, MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT, OBJECT_TITLE_LIMIT, RECIPE_MAX_LENGTH,
    SLUG_MAX_LENGTH, TAG_MAX_LENGTH, URL_TOKEN_MAX_LENGTH
)

User = get_user_model()


class UserRecipeRelationModel(models.Model):
    """
    Абстрактная модель.
    Добавляет поля автора и рецепта, для связывающих их моделей.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='%(class)ss'
    )
    recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='%(class)s_set'
    )

    class Meta:
        abstract = True
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_%(class)s'
            ),
        )

    def __str__(self):
        return f'{self.user} - {self.recipe}.'


class Tag(models.Model):
    name = models.CharField(
        max_length=TAG_MAX_LENGTH, unique=True, verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=SLUG_MAX_LENGTH, unique=True, verbose_name='Идентификатор'
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name[:OBJECT_TITLE_LIMIT]


class Ingredient(models.Model):
    name = models.CharField(
        max_length=INGREDIENT_MAX_LENGTH, verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:OBJECT_TITLE_LIMIT]


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор'
    )
    name = models.CharField(
        max_length=RECIPE_MAX_LENGTH, verbose_name='Название'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(MIN_COOKING_TIME),),
        verbose_name='Время приготовления (в минутах)'
    )
    image = models.ImageField(
        upload_to='recipes/images/', null=True, default=None,
        verbose_name='Картинка'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    short_link_token = models.CharField(
        max_length=URL_TOKEN_MAX_LENGTH, blank=True, null=True, unique=True
    )
    created = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ('-created',)

    def generate_short_link_token(self):
        max_attempts = 100
        attempts = 0

        while attempts < max_attempts:
            short_link_token = get_random_string(3)

            if not Recipe.objects.filter(
                short_link_token=short_link_token
            ).exists():
                return short_link_token

            attempts += 1

        return get_random_string(4)

    def save(self, *args, **kwargs):
        if not self.short_link_token:
            self.short_link_token = self.generate_short_link_token()
        super().save(*args, **kwargs)

    @property
    def short_link(self):
        return f'{settings.HOST_NAME}/s/{self.short_link_token}/'

    def __str__(self):
        return self.name[:OBJECT_TITLE_LIMIT]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(MIN_INGREDIENT_AMOUNT),),
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            ),
        )

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}.'


class Favorite(UserRecipeRelationModel):

    class Meta(UserRecipeRelationModel.Meta):
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(UserRecipeRelationModel):

    class Meta(UserRecipeRelationModel.Meta):
        verbose_name = 'cписок покупок'
        verbose_name_plural = 'Списки покупок'
