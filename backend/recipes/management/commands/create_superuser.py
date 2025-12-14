from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates a superuser with default credentials'

    def handle(self, *args, **options):
        email = 'admin@foodgram.com'
        username = 'admin'
        password = 'adminpassword'

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='Foodgram'
            )
            self.stdout.write(self.style.SUCCESS(
                f'Superuser created with email: {email}'))
        else:
            self.stdout.write(self.style.WARNING(
                f'Superuser with email {email} already exists'))
