from django.core.management.base import BaseCommand
from vehicles.models import User


class Command(BaseCommand):
    help = "Create initial admin user"

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                password="admin123",
                email="admin@fleettrack.com",
                role="admin",
            )
            self.stdout.write(
                self.style.SUCCESS("Admin user created: admin / admin123")
            )
        else:
            self.stdout.write("Admin user already exists.")

        if not User.objects.filter(username="staff").exists():
            User.objects.create_user(
                username="staff",
                password="staff123",
                email="staff@fleettrack.com",
                role="staff",
            )
            self.stdout.write(
                self.style.SUCCESS("Staff user created: staff / staff123")
            )
        else:
            self.stdout.write("Staff user already exists.")
