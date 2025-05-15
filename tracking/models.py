from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from recommendations.gorse_client import GorseClient

class UserFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    feedback_type = models.CharField(max_length=20)  # view, click, cart, purchase
    timestamp = models.DateTimeField(auto_now_add=True)
    synced_to_gorse = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'product']),
            models.Index(fields=['synced_to_gorse']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.feedback_type} - {self.product.name}"
    
    def sync_to_gorse(self):
        """Sync this feedback to Gorse"""
        try:
            gorse_client = GorseClient()
            gorse_client.insert_feedback(
                str(self.user.id),
                self.product.gorse_item_id,
                self.feedback_type
            )
            self.synced_to_gorse = True
            self.save()
            return True
        except Exception as e:
            print(f"Error syncing feedback to Gorse: {e}")
            return False

def record_user_feedback(user, product, feedback_type):
    """Utility function to record user feedback and sync with Gorse"""
    if not user.is_authenticated:
        return None
    
    # Record feedback in our database
    feedback = UserFeedback.objects.create(
        user=user,
        product=product,
        feedback_type=feedback_type
    )
    
    # Sync with Gorse
    feedback.sync_to_gorse()
    
    return feedback