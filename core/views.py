from django.shortcuts import render
from products.models import Category, Product
from recommendations.gorse_client import GorseClient
from difflib import SequenceMatcher

def home(request):
    categories = Category.objects.all()
    
    # Get popular products using gorse.io
    gorse_client = GorseClient()
    
    try:
        popular_item_ids = gorse_client.get_user_neighbors(request.user.id,n=8)
        popular_products = Product.objects.filter(gorse_item_id__in=popular_item_ids)
        print(f"core views popular_item_ids: {popular_item_ids} popular_products: {popular_products}")
    except Exception as e:
        print(f"Error getting popular products: {e}")
        popular_products = Product.objects.filter(available=True)[:12]
    
    # Get recommended products if user is authenticated
    recommended_products = []
    if request.user.is_authenticated:
        try:
            recommended_item_ids = gorse_client.get_recommend_items(request.user.id, n=8)
            recommended_products = Product.objects.filter(gorse_item_id__in=recommended_item_ids)
            print(f"core views recommended_item_ids: {recommended_item_ids} recommended_products: {recommended_products}")
        except Exception as e:
            print(f"Error getting recommended products: {e}")
    
    # Function to calculate string similarity
    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()
    
    # Function to filter out similar products
    def filter_similar_products(products_list, similarity_threshold=0.7):
        filtered_products = []
        product_names = []
        
        for product in products_list:
            # Check if this product name is too similar to any we've already added
            is_similar = False
            for existing_name in product_names:
                if similar(product.name.lower(), existing_name.lower()) > similarity_threshold:
                    is_similar = True
                    break
            
            # If not too similar, add it to our filtered list
            if not is_similar:
                filtered_products.append(product)
                product_names.append(product.name)
                
            # Stop once we have 8 unique products
            if len(filtered_products) >= 8:
                break
        
        return filtered_products
    
    # Featured products (filter from popular products or get some diverse products)
    if len(popular_products) < 4:
        # Get more products than needed so we can filter similar ones
        featured_candidates = Product.objects.filter(available=True)[:20]
        featured_products = filter_similar_products(featured_candidates)
    else:
        # Filter similar products from popular products
        featured_products = filter_similar_products(popular_products)
        
        # If we still don't have enough products after filtering, add some more diverse ones
        if len(featured_products) < 8:
            additional_products = Product.objects.filter(available=True).exclude(id__in=[p.id for p in featured_products])[:12]
            featured_products.extend(filter_similar_products(additional_products, 0.6)[:8-len(featured_products)])
    
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