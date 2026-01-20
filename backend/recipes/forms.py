from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet


class RecipeIngredientFormSet(BaseInlineFormSet):
    """FormSet для ингредиентов рецепта с валидацией."""

    def clean(self):
        super().clean()

        if all(
            not form.cleaned_data or form.cleaned_data.get('DELETE', False)
            for form in self.forms
        ):
            raise ValidationError(
                'Рецепт должен содержать хотя бы один ингредиент.'
            )
