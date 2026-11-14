"""Seed the database with restaurants, menus, dineout venues and the demo user.

Run:  python manage.py seed
"""
from django.core.management.base import BaseCommand

from api.seed import seed_all


class Command(BaseCommand):
    help = "Seed FoodieExpress demo data (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Re-create rows even if data exists")

    def handle(self, *args, **options):
        seed_all(force=options["force"])
        self.stdout.write(self.style.SUCCESS("FoodieExpress database seeded."))
