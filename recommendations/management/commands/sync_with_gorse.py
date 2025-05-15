from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Run all sync commands with Gorse'

    def handle(self, *args, **options):
        self.stdout.write('Starting Gorse synchronization...')
        
        # Sync products
        self.stdout.write('\n--- Syncing products ---')
        call_command('sync_gorse')
        
        # Sync users
        self.stdout.write('\n--- Syncing users ---')
        call_command('sync_users_with_gorse')
        
        # Sync feedback
        self.stdout.write('\n--- Syncing feedback ---')
        call_command('sync_feedback')
        
        self.stdout.write(self.style.SUCCESS('\nGorse synchronization completed!'))