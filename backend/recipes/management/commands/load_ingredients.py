import os
from django.core.management.base import BaseCommand
from recipes.models import Ingredient
import csv
import json


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из CSV или JSON файла'

    def handle(self, *args, **kwargs):
        csv_path = '/app/data/ingredients.csv'
        json_path = '/app/data/ingredients.json'

        if os.path.exists(csv_path):
            self.load_from_csv(csv_path)
        elif os.path.exists(json_path):
            self.load_from_json(json_path)
        else:
            self.stdout.write(self.style.ERROR(
                'Файл с ингредиентами не найден'))
