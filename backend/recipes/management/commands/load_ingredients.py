import csv
import os

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Loads ingredients from CSV file'

    def handle(self, *args, **options):
        file_path = os.path.join('data', 'ingredients.csv')
        with open(file_path, encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name.strip(),
                    measurement_unit=measurement_unit.strip()
                )
        self.stdout.write(self.style.SUCCESS(
            'Ingredients loaded successfully'))
