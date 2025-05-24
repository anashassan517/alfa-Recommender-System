from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from recommendations.gorse_client import GorseClient
from users.models import UserProfile
import random

class Command(BaseCommand):
    help = 'Synchronize users with Gorse recommender system'

    def handle(self, *args, **options):
        gorse_client = GorseClient()
        users = User.objects.all()
        print("Users for syncing:",users)
        
        self.stdout.write(f'Syncing {users.count()} users with Gorse')
        
        for user in users:
            try:
                # Get or create profile
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                # Get interests from profile or generate random ones
                interests = []
                if profile.interests:
                    interests = profile.interests.split(' | ')
                else:
                    # Generate random interests for demonstration
                    interests = self._get_random_interests()
                    profile.interests = ' | '.join(interests)
                    profile.save()
                
                # Create user data for Gorse
                user_data = {
                    'UserId': str(user.id),
                    'Labels': interests,
                    'Comment': user.username,
                    'Subscribe': []  # You can customize this based on your needs
                }
                
                # Insert or update user in Gorse
                success = gorse_client.insert_user(user_data)
                if success:
                    self.stdout.write(f'Synced user: {user.username}')
                else:
                    self.stdout.write(self.style.WARNING(f'Failed to sync user: {user.username}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error syncing user {user.id}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('User sync completed!'))
    
    def _get_random_interests(self):
        """Generate random interests for demo purposes"""
        possible_interests = [
          "led tv", "electronics", "Apple", "washing machine", "kitchen items", "samsung", 
            "laptops", "mobiles", "travel", "watches", "air conditioner AC"
        ]
        return random.sample(possible_interests, random.randint(2, 5))