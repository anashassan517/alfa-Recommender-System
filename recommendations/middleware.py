from .gorse_client import GorseClient

class UserFeedbackMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.gorse_client = GorseClient()

    def __call__(self, request):
        response = self.get_response(request)
        
        # Process after view is executed
        if request.user.is_authenticated and request.method == 'POST':
            # Track purchases on order completion
            if request.path.endswith('/cart/') and hasattr(request, 'session'):
                cart = request.session.get('cart', {})
                for product_id, item in cart.items():
                    try:
                        # Record purchase feedback
                        self.gorse_client.insert_feedback(
                            str(request.user.id),
                            item.get('gorse_item_id', ''),
                            'purchase'
                        )
                    except Exception as e:
                        print(f"Error recording purchase feedback: {e}")
        
        return response