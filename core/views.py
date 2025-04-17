# from django.shortcuts import render
# from products.models import Category, Product
# from recommendations.gorse_client import GorseClient

# def home(request):
#     categories = Category.objects.all()
    
#     # Get popular products using gorse.io
#     gorse_client = GorseClient()
#     popular_item_ids = gorse_client.get_popular_items(n=8)
    
#     # Get recommended products if user is authenticated
#     recommended_products = []
#     if request.user.is_authenticated:
#         recommended_item_ids = gorse_client.get_recommend_items(request.user.id, n=8)
#         recommended_products = Product.objects.filter(gorse_item_id__in=recommended_item_ids)
    
#     # Get popular products from the database using item_ids from gorse
#     popular_products = Product.objects.filter(gorse_item_id__in=popular_item_ids)
    
#     # Featured products (just get some products if gorse doesn't return enough)
#     if len(popular_products) < 4:
#         featured_products = Product.objects.filter(available=True)[:8]
#     else:
#         featured_products = popular_products
    
#     context = {
#         'categories': categories,
#         'featured_products': featured_products,
#         'recommended_products': recommended_products
#     }
#     return render(request, 'core/home.html', context)

# def about(request):
#     return render(request, 'core/about.html')

# def contact(request):
#     return render(request, 'core/contact.html')
from django.shortcuts import render
from products.models import Category, Product
from recommendations.gorse_client import GorseClient

def home(request):
    categories = Category.objects.all()
    
    # Get popular products using gorse.io
    gorse_client = GorseClient()
    
    try:
        popular_item_ids = gorse_client.get_popular_items(n=8)
        popular_products = Product.objects.filter(gorse_item_id__in=popular_item_ids)
        print(f"core views popular_item_ids: {popular_item_ids} popular_products: {popular_products}")
    except Exception as e:
        print(f"Error getting popular products: {e}")
        popular_products = Product.objects.filter(available=True)[:8]
    
    # Get recommended products if user is authenticated
    recommended_products = []
    if request.user.is_authenticated:
        try:
            recommended_item_ids = gorse_client.get_recommend_items(request.user.id, n=8)
            recommended_products = Product.objects.filter(gorse_item_id__in=recommended_item_ids)
            print(f"core views recommended_item_ids: {recommended_item_ids} recommended_products: {recommended_products}")
        except Exception as e:
            print(f"Error getting recommended products: {e}")
    
    # Featured products (just get some products if gorse doesn't return enough)
    if len(popular_products) < 4:
        featured_products = Product.objects.filter(available=True)[:8]
    else:
        featured_products = popular_products
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'recommended_products': recommended_products
    }
    return render(request, 'core/home.html', context)

def about(request):
    categories = Category.objects.all()
    return render(request, 'core/about.html', {'categories': categories})

def contact(request):
    categories = Category.objects.all()
    return render(request, 'core/contact.html', {'categories': categories})