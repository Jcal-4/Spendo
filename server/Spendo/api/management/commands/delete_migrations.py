from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Delete all migration files except __init__.py in the migrations directory.'

    def handle(self, *args, **options):
        migrations_dir = os.path.join(os.path.dirname(__file__), '../../../api/migrations')
        deleted = 0
        for filename in os.listdir(migrations_dir):
            if filename != '__init__.py' and filename.endswith('.py'):
                file_path = os.path.join(migrations_dir, filename)
                os.remove(file_path)
                self.stdout.write(self.style.SUCCESS(f'Removed {file_path}'))
                deleted += 1
        if deleted == 0:
            self.stdout.write(self.style.WARNING('No migration files found to delete.'))
        else:
            self.stdout.write(self.style.SUCCESS('All migration files (except __init__.py) have been deleted.'))
