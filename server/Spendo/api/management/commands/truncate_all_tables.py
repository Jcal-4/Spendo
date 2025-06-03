from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection

class Command(BaseCommand):
    help = 'Truncate all tables in the database (development use only!)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Truncating all tables...'))
        with connection.cursor() as cursor:
            for model in apps.get_models():
                table = model._meta.db_table
                try:
                    cursor.execute(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE;')
                    self.stdout.write(self.style.SUCCESS(f'Truncated table: {table}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Skipped table: {table} (reason: {e})'))
        self.stdout.write(self.style.SUCCESS('All tables truncated (or skipped if missing).'))
