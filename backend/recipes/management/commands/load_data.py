import csv
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Ingredient

User = get_user_model()


class Command(BaseCommand):
    help = 'Загрузка данных из CSV файлов в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='Путь к директории с CSV файлами'
        )

    def handle(self, *args, **kwargs):
        path = kwargs['path'] or 'static/data/'
        self.stdout.write(f'Загрузка данных из директории: {path}')

        try:
            with transaction.atomic():
                self.load_ingredients(path)
            self.stdout.write(self.style.SUCCESS('Данные успешно загружены'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при загрузке данных: {str(e)}')
            )

    def load_ingredients(self, path):
        self.stdout.write('Загрузка ингредиентов...')
        with open(
            Path(path) / 'ingredients.csv', 'r', encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                Ingredient.objects.update_or_create(
                    name=row['name'],
                    defaults={
                        'measurement_unit': row['measurement_unit']
                    }
                )
