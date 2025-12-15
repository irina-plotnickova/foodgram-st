import os
import csv
import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из JSON файла'

    def handle(self, *args, **options):
        possible_paths = [
            '/app/data/ingredients.json',
            'data/ingredients.json',
            '../data/ingredients.json',
        ]

        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                self.stdout.write(f"Найден файл: {path}")
                break

        if not file_path:
            self.stdout.write(self.style.ERROR(
                'Файл с ингредиентами не найден'))
            return

        if file_path.endswith('.csv'):
            self.load_from_csv(file_path)
        elif file_path.endswith('.json'):
            self.load_from_json(file_path)

    def load_from_csv(self, file_path):
        with open(file_path, encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 2:
                    name, measurement_unit = row
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
            self.stdout.write(self.style.SUCCESS(
                'Ингредиенты загружены из CSV'))

    def load_from_json(self, file_path):
        with open(file_path, encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
            self.stdout.write(self.style.SUCCESS(
                'Ингредиенты загружены из JSON'))
