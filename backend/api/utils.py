import io

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFError, TTFont
from reportlab.pdfgen import canvas

from .constants import (
    BOTTOM_MARGIN, DOUBLE_LINE_HEIGHT, FONT_SIZE, LEFT_MARGIN, LINE_HEIGHT,
    PARAGRAPH_INDENTATION, RECIPE_TITLE_LIMIT, RIGHT_MARGIN, TITLE_FONT_SIZE,
    TOP_MARGIN
)


def generate_shopping_list_pdf(recipes_queryset, ingredients_queryset):
    """Функция генерирует PDF со списком покупок."""

    with io.BytesIO() as buffer:
        pdf = canvas.Canvas(buffer, pagesize=A4)

        try:
            pdfmetrics.registerFont(TTFont(
                'DejaVu', 'docs/DejaVuSans.ttf'
            ))
            font_name = 'DejaVu'
        except TTFError:
            font_name = 'Helvetica'

        y = TOP_MARGIN

        pdf.setFont(font_name, TITLE_FONT_SIZE)
        pdf.drawString(PARAGRAPH_INDENTATION, y, 'Список покупок')
        y -= DOUBLE_LINE_HEIGHT

        pdf.setFont(font_name, FONT_SIZE)
        pdf.drawString(LEFT_MARGIN, y, 'Рецепты:')
        y -= LINE_HEIGHT

        for i, recipe in enumerate(recipes_queryset, 1):
            if y < BOTTOM_MARGIN:
                pdf.showPage()
                pdf.setFont(font_name, FONT_SIZE)
                y = TOP_MARGIN

            recipe_name = recipe.name
            if len(recipe_name) > RECIPE_TITLE_LIMIT:
                recipe_name = recipe_name[:RECIPE_TITLE_LIMIT] + '...'

            pdf.drawString(PARAGRAPH_INDENTATION, y, f'{i}. {recipe_name}')
            y -= LINE_HEIGHT

        pdf.line(LEFT_MARGIN, y, RIGHT_MARGIN, y)
        y -= LINE_HEIGHT

        pdf.drawString(LEFT_MARGIN, y, 'Ингредиенты:')
        y -= LINE_HEIGHT

        for ingredient in ingredients_queryset:
            if y < BOTTOM_MARGIN:
                pdf.showPage()
                pdf.setFont(font_name, FONT_SIZE)
                y = TOP_MARGIN

            text = (
                f'• {ingredient["ingredient__name"]} - '
                f'{ingredient["total_amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}'
            )

            pdf.drawString(PARAGRAPH_INDENTATION, y, text)
            y -= LINE_HEIGHT

        pdf.line(LEFT_MARGIN, y, RIGHT_MARGIN, y)
        y -= LINE_HEIGHT

        pdf.drawString(
            LEFT_MARGIN, y,
            f'Итого наименований ингредиентов: {ingredients_queryset.count()}'
        )
        y -= DOUBLE_LINE_HEIGHT

        pdf.drawString(
            LEFT_MARGIN, y,
            'Приятных покупок! Возвращайтесь к нам за новыми рецептами!'
        )

        pdf.save()
        buffer.seek(0)

        return buffer.getvalue()
