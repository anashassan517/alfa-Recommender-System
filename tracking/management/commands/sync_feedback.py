from django.core.management.base import BaseCommand
from tracking.models import UserFeedback

class Command(BaseCommand):
    help = 'Synchronize unsynced feedback with Gorse'

    def handle(self, *args, **options):
        unsynced_feedback = UserFeedback.objects.filter(synced_to_gorse=False)
        count = unsynced_feedback.count()
        
        self.stdout.write(f'Found {count} unsynced feedback records')
        
        success_count = 0
        for feedback in unsynced_feedback:
            if feedback.sync_to_gorse():
                success_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully synced {success_count} out of {count} feedback records'))