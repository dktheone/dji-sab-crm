from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = "Delete all users and related records, then create a superuser SAB_001"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting all users...")

        # Delete all users (cascade will remove groups & permissions relations)
        User.objects.all().delete()

        self.stdout.write("All users deleted successfully.")

        # Create a new superuser
        username = "SAB0001"
        email = "sab0001@example.com"
        password = "ChangeMe123!"  # ⚠️ update after creation

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully ✅"))
        else:
            self.stdout.write(self.style.WARNING(f"Superuser '{username}' already exists ❗"))
