import io

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFError, TTFont
from reportlab.pdfgen import canvas


def generate_shopping_list_pdf(ingredients_queryset):
    """Функция генерирует PDF со списком покупок."""

    with io.BytesIO() as buffer:
        pdf = canvas.Canvas(buffer, pagesize=A4)

        try:
            pdfmetrics.registerFont(TTFont(
                'DejaVu', 'static/fonts/DejaVuSans.ttf'
            ))
            font_name = 'DejaVu'
        except TTFError:
            font_name = 'Helvetica'

        LEFT_MARGIN = 50
        TOP_MARGIN = 750
        LINE_HEIGHT = 20
        y = TOP_MARGIN

        pdf.setFont(font_name, 16)
        pdf.drawString(LEFT_MARGIN, y, 'Список покупок')

        y -= LINE_HEIGHT * 2
        pdf.setFont(font_name, 12)

        for ingredient in ingredients_queryset:
            if y < 50:
                pdf.showPage()
                pdf.setFont(font_name, 12)
                y = TOP_MARGIN

            text = (
                f'• {ingredient['ingredient__name']} - '
                f'{ingredient['total_amount']} '
                f'{ingredient['ingredient__measurement_unit']}'
            )
            print(text)

            pdf.drawString(LEFT_MARGIN, y, text)
            y -= LINE_HEIGHT

        pdf.line(LEFT_MARGIN, y, 550, y)
        y -= LINE_HEIGHT
        pdf.drawString(
            LEFT_MARGIN, y, f'Итого позиций: {ingredients_queryset.count()}'
        )
        y -= LINE_HEIGHT * 2
        pdf.drawString(
            LEFT_MARGIN, y,
            'Приятных покупок! Возвращайтесь к нам за новыми рецептами!'
        )

        pdf.save()
        buffer.seek(0)

        return buffer.getvalue()
