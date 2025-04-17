from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from recommendations.gorse_client import GorseClient
from cart.forms import CartAddProductForm

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    context = {
        'category': category,
        'categories': categories,
        'products': products
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    
    # Record view feedback in gorse if user is authenticated
    if request.user.is_authenticated:
        gorse_client = GorseClient()
        gorse_client.insert_feedback(
            str(request.user.id), 
            product.gorse_item_id, 
            'view'
        )
    
    # Get similar products recommendation from gorse.io
    gorse_client = GorseClient()
    
    # Using get_item_neighbors instead of get_similar_items
    similar_items_response = gorse_client.get_item_neighbors(product.gorse_item_id, n=4)
    
    # Extract item IDs - handle both string IDs and dictionary responses
    similar_item_ids = []
    for item in similar_items_response:
        if isinstance(item, dict) and 'ItemId' in item:
            similar_item_ids.append(item['ItemId'])
        elif isinstance(item, str):
            similar_item_ids.append(item)
    
    similar_products = Product.objects.filter(gorse_item_id__in=similar_item_ids)
    
    # If not enough similar products from gorse, supplement with products from same category
    if similar_products.count() < 4:
        category_products = Product.objects.filter(
            category=product.category, 
            available=True
        ).exclude(id=product.id)[:4-similar_products.count()]
        similar_products = list(similar_products) + list(category_products)
    
    context = {
        'product': product,
        'cart_product_form': cart_product_form,
        'similar_products': similar_products
    }
    return render(request, 'products/product_detail.html', context)