from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from recommendations.gorse_client import GorseClient
import random

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Add any additional user fields here
    interests = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"

    def get_random_interests(self):
        """Generate random interests for demo purposes"""
        possible_interests = [
          "led tv", "electronics", "Apple", "washing machine", "kitchen items", "samsung", 
            "laptops", "mobiles", "travel", "watches", "air conditioner AC"
        ]
        # possible_interests = [
        #   "led tv", "electronics", "digital goods", "hunarmand", "kitchen items", "fans", 
        #     "bikes", "mobiles", "travel", "washing machines", "online subscription", "reading",
        #     "clothing", "entertainment", "outdoors", "fashion"
        # ]
        return random.sample(possible_interests, random.randint(2, 5))

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Signal to create or update user profile when User is saved"""
    if created:
        profile = UserProfile.objects.create(user=instance)
        
        # Generate random interests for demo
        interests = profile.get_random_interests()
        profile.interests = '|'.join(interests)
        profile.save()
        
        # Sync with Gorse
        sync_user_with_gorse(instance, interests)
    else:
        # Update existing profile
        if hasattr(instance, 'profile'):
            instance.profile.save()
            
            # Get interests from profile
            interests = []
            if instance.profile.interests:
                interests = instance.profile.interests.split('|')
                
            # Sync with Gorse
            sync_user_with_gorse(instance, interests)

def sync_user_with_gorse(user, interests=None):
    """Sync user data with Gorse"""
    try:
        gorse_client = GorseClient()
        
        # Prepare user data
        user_data = {
            'UserId': str(user.id),
            'Labels': interests or [],
            'Comment': user.username,
            'Subscribe': []  # You can customize this based on your needs
        }
        
        # Insert user into Gorse
        gorse_client.insert_user(user_data)
    except Exception as e:
        print(f"Error syncing user with Gorse: {e}")
