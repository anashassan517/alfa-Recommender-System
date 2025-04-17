from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .gorse_client import GorseClient
from products.models import Product, Category
import logging

logger = logging.getLogger(__name__)


def latest_items(request):
    """Show the latest items added to the system"""
    gorse_client = GorseClient()
    categories = Category.objects.all()
    
    # Get category filter if provided
    category_slug = request.GET.get('category', '')
    category = None
    category_name = ''
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        category_name = category.name
    
    # Get latest item IDs
    latest_items_response = gorse_client.get_latest_items(category=category_name, n=50)
    print(f"latest_items_response: {latest_items_response}")
    
    # Extract item IDs - handle both string IDs and dictionary responses
    latest_item_ids = []
    for item in latest_items_response:
        if isinstance(item, dict) and 'id' in item:
            latest_item_ids.append(item['id'])
        elif isinstance(item, str):
            latest_item_ids.append(item)
    
    # Retrieve the actual products from the database
    products_dict = {}
    if latest_item_ids:
        products = Product.objects.filter(gorse_item_id__in=latest_item_ids)
        # Create a dictionary of products for proper ordering
        products_dict = {product.gorse_item_id: product for product in products}
    
    # Maintain the order from Gorse
    latest_products = [products_dict.get(item_id) for item_id in latest_item_ids if item_id in products_dict]
    
    context = {
        'recommended_products': latest_products,
        'categories': categories,
        'selected_category': category,
        'recommendation_type': 'Latest Items'
    }
    return render(request, 'recommendations/recommendation_list.html', context)

# Use the same fix for popular_items and user_recommendations methods
def popular_items(request):
    """Show the most popular items"""
    gorse_client = GorseClient()
    categories = Category.objects.all()
    
    # Get category filter if provided
    category_slug = request.GET.get('category', '')
    category = None
    category_name = ''
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        category_name = category.name
    
    # Get popular item IDs
    popular_items_response = gorse_client.get_popular_items(category=category_name, n=50)
    
    # Extract item IDs - handle both string IDs and dictionary responses
    popular_item_ids = []
    for item in popular_items_response:
        if isinstance(item, dict) and 'id' in item:
            popular_item_ids.append(item['id'])
        elif isinstance(item, str):
            popular_item_ids.append(item)
    
    # Retrieve the actual products from the database
    products_dict = {}
    if popular_item_ids:
        products = Product.objects.filter(gorse_item_id__in=popular_item_ids)
        # Create a dictionary of products for proper ordering
        products_dict = {product.gorse_item_id: product for product in products}
    
    # Maintain the order from Gorse
    popular_products = [products_dict.get(item_id) for item_id in popular_item_ids if item_id in products_dict]
    
    context = {
        'recommended_products': popular_products,
        'categories': categories,
        'selected_category': category,
        'recommendation_type': 'Popular Items'
    }
    return render(request, 'recommendations/recommendation_list.html', context)

@login_required
def user_recommendations(request):
    """Show personalized recommendations for the current user"""
    gorse_client = GorseClient()
    categories = Category.objects.all()
    
    # Get category filter if provided
    category_slug = request.GET.get('category', '')
    category = None
    category_name = ''
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        category_name = category.name
    
    # Get recommended item IDs for the current user
    recommended_items_response = gorse_client.get_recommend_items(str(request.user.id), category=category_name, n=50)
    
    # Extract item IDs - handle both string IDs and dictionary responses
    recommended_item_ids = []
    for item in recommended_items_response:
        if isinstance(item, dict) and 'id' in item:
            recommended_item_ids.append(item['id'])
        elif isinstance(item, str):
            recommended_item_ids.append(item)
    
    # Retrieve the actual products from the database
    products_dict = {}
    if recommended_item_ids:
        products = Product.objects.filter(gorse_item_id__in=recommended_item_ids)
        # Create a dictionary of products for proper ordering
        products_dict = {product.gorse_item_id: product for product in products}
    
    # Maintain the order from Gorse recommendations
    recommended_products = [products_dict.get(item_id) for item_id in recommended_item_ids if item_id in products_dict]
    
    context = {
        'recommended_products': recommended_products,
        'categories': categories,
        'selected_category': category,
        'recommendation_type': 'For You'
    }
    return render(request, 'recommendations/recommendation_list.html', context)

def similar_items(request, product_id):
    """Show items similar to the given product"""
    gorse_client = GorseClient()
    categories = Category.objects.all()
    product = get_object_or_404(Product, id=product_id)
    
    # Get category filter if provided
    category_slug = request.GET.get('category', '')
    category = None
    category_name = ''
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        category_name = category.name
    
    # Get similar item IDs
    similar_items_response = gorse_client.get_item_neighbors(product.gorse_item_id, category=category_name, n=25)
    
    # Extract item IDs - handle both string IDs and dictionary responses
    similar_item_ids = []
    for item in similar_items_response:
        if isinstance(item, dict) and 'id' in item:
            similar_item_ids.append(item['id'])
        elif isinstance(item, str):
            similar_item_ids.append(item)
    
    # Retrieve the actual products from the database
    products_dict = {}
    if similar_item_ids:
        products = Product.objects.filter(gorse_item_id__in=similar_item_ids)
        # Create a dictionary of products for proper ordering
        products_dict = {product.gorse_item_id: product for product in products}
    
    # Maintain the order from Gorse
    similar_products = [products_dict.get(item_id) for item_id in similar_item_ids if item_id in products_dict]
    
    context = {
        'recommended_products': similar_products,
        'categories': categories,
        'selected_category': category,
        'source_product': product,
        'recommendation_type': f'Similar to {product.name}'
    }
    return render(request, 'recommendations/recommendation_list.html', context)

def explore_recommendations(request):
    """Explore different recommendation types"""
    categories = Category.objects.all()
    
    context = {
        'categories': categories,
    }
    return render(request, 'recommendations/explore.html', context)

# Dashboard item neighbors
def get_dashboard_item_neighbors(self, item_id, n=10, offset=0):
        """Get dashboard neighbors data for an item"""
        endpoint = f"/api/item/{item_id}/neighbors"
        
        url = f"{self.base_url}{endpoint}"
        params = {'n': n, 'offset': offset}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return self._log_response(endpoint, response.json(), params)
        except Exception as e:
            logger.error(f"Error getting dashboard item neighbors: {e}")
            print(f"Error getting dashboard item neighbors: {e}")
            return []    

def dashboard_item_neighbors(request, product_id):
    """Get detailed dashboard information about item neighbors"""
    gorse_client = GorseClient()
    product = get_object_or_404(Product, id=product_id)
    
    # Get dashboard item neighbors data
    neighbors_data=gorse_client.get_item_neighbors(product.gorse_item_id, n=20)
    
    # Get the actual products
    item_ids = [item.get('id', '') for item in neighbors_data if 'id' in item]
    products = Product.objects.filter(gorse_item_id__in=item_ids)
    products_dict = {product.gorse_item_id: product for product in products}
    
    # Enhance the neighbors data with product information
    for item in neighbors_data:
        item_id = item.get('id', '')
        if item_id in products_dict:
            item['product'] = products_dict[item_id]
    
    context = {
        'source_product': product,
        'neighbors_data': neighbors_data,
        'categories': Category.objects.all(),
    }
    return render(request, 'recommendations/dashboard_neighbors.html', context)

# API endpoint for AJAX recommendations
def get_recommendations_json(request):
    """Get recommendations in JSON format for AJAX requests"""
    gorse_client = GorseClient()
    
    rec_type = request.GET.get('type', 'popular')
    category = request.GET.get('category', '')
    item_id = request.GET.get('item_id', '')
    user_id = request.user.id if request.user.is_authenticated else None
    limit = int(request.GET.get('limit', 10))
    
    items_response = []
    
    if rec_type == 'popular':
        items_response = gorse_client.get_popular_items(category=category, n=limit)
    elif rec_type == 'latest':
        items_response = gorse_client.get_latest_items(category=category, n=limit)
        print(f"get_recommendations_json latest items_response: {items_response}")
    elif rec_type == 'similar' and item_id:
        items_response = gorse_client.get_item_neighbors(item_id, category=category, n=limit)
    elif rec_type == 'recommended' and user_id:
        items_response = gorse_client.get_recommend_items(str(user_id), category=category, n=limit)
    
    # Extract item IDs from the response
    item_ids = []
    for item in items_response:
        if isinstance(item, dict) and 'id' in item:
            item_ids.append(item['id'])
        elif isinstance(item, str):
            item_ids.append(item)
    
    products = []
    if item_ids:
        print(f"get_recommendations_json item_ids: {item_ids}")
        product_objs = Product.objects.filter(gorse_item_id__in=item_ids)
        products_dict = {p.gorse_item_id: p for p in product_objs}
        
        for item_id in item_ids:
            if item_id in products_dict:
                product = products_dict[item_id]
                products.append({
                    'id': product.id,
                    'name': product.name,
                    'price': str(product.price),
                    'image_url': product.image.url if product.image else None,
                    'url': product.get_absolute_url(),
                })
    
    return JsonResponse({'products': products})