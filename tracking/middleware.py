from products.models import Product
from .models import record_user_feedback

class UserActionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Process after view is executed
        if request.user.is_authenticated:
            # Capture product clicks (when navigating to a product detail page)
            if request.path.startswith('/products/') and request.method == 'GET':
                parts = request.path.strip('/').split('/')
                if len(parts) >= 3 and parts[0] == 'products':
                    try:
                        product_id = int(parts[1])
                        product = Product.objects.get(id=product_id)
                        record_user_feedback(request.user, product, 'click')
                    except (ValueError, Product.DoesNotExist):
                        pass
            
            # Track purchases on order completion
            if request.path.endswith('/checkout/complete/') and request.method == 'GET':
                if hasattr(request, 'session') and 'order_id' in request.session:
                    # Assuming you store cart items in the session during checkout
                    cart = request.session.get('cart', {})
                    for product_id, item in cart.items():
                        try:
                            product = Product.objects.get(id=product_id)
                            record_user_feedback(request.user, product, 'purchase')
                        except Product.DoesNotExist:
                            pass
        
        return response