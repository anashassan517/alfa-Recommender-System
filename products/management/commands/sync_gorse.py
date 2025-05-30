# import json
# import os
# from django.core.management.base import BaseCommand
# from django.conf import settings
# from products.models import Product
# import requests

# class Command(BaseCommand):
#     help = 'Synchronize products with Gorse recommender system'

#     def handle(self, *args, **options):
#         if not settings.GORSE_API_URL:
#             self.stdout.write(self.style.ERROR('GORSE_API_URL is not set in settings'))
#             return
        
#         gorse_client = GorseClient()
        
#         # Get all available products
#         products = Product.objects.filter(available=True)
        
#         self.stdout.write(f'Syncing {products.count()} products with Gorse')
#         self.stdout.write(f'Products Details : {products} ')
        
#         for product in products:
#             try:
#                 # first display the product details id, category
#                 self.stdout.write(f'Product ID: {product.id}, Category: {product.category.name}')
#                 # Create item data for Gorse
#                 item_data = {
#                     'ItemId': product.gorse_item_id,
#                     'categories': [product.category.name],
#                     'Labels': [],
#                     'Timestamp': product.created.timestamp() if product.created else '',
#                     'Comment': product.name,
#                     'IsHidden': not product.available
#                 }
                
#                 # Insert or update item in Gorse
#                 success = gorse_client.insert_item(item_data)
#                 if success:
#                     self.stdout.write(f'Synced product: {product.name}')
#                 else:
#                     self.stdout.write(self.style.WARNING(f'Failed to sync product: {product.name}'))
                
#             except Exception as e:
#                 self.stdout.write(self.style.ERROR(f'Error syncing product {product.id}: {str(e)}'))
        
#         self.stdout.write(self.style.SUCCESS('Product sync completed!'))

# class GorseClient:
#     def __init__(self):
#         self.base_url = settings.GORSE_API_URL
#         self.api_key = settings.GORSE_API_KEY
#         self.headers = {}
#         if self.api_key:
#             self.headers['X-API-Key'] = self.api_key
    
#     def insert_item(self, item_data):
#         """
#         Insert or update an item in Gorse
#         """
#         url = f"{self.base_url}/apia/item"
#         try:
#             response = requests.post(url, json=item_data, headers=self.headers)
#             response.raise_for_status()
#             return True
#         except Exception as e:
#             print(f"Error inserting item: {e}")
#             return False


#### working code:
# import json
# import os
# from django.core.management.base import BaseCommand
# from django.conf import settings
# from products.models import Product
# import requests
# from datetime import datetime

# class Command(BaseCommand):
#     help = 'Synchronize products with Gorse recommender system'

#     def handle(self, *args, **options):
#         if not settings.GORSE_API_URL:
#             self.stdout.write(self.style.ERROR('GORSE_API_URL is not set in settings'))
#             return
        
#         gorse_client = GorseClient()
        
#         # Get all available products
#         products = Product.objects.filter()
        
#         self.stdout.write(f'Syncing {products.count()} products with Gorse')
        
#         for product in products:
#             try:
#                 # Create labels list with all relevant product information
#                 labels = [
#                     product.category.name,  # Main category
#                 ]
                
#                 # Add price range labels
#                 price = float(product.price)
#                 if price < 1000:
#                     labels.append("price_under_1k")
#                 elif price < 5000:
#                     labels.append("price_1k_5k")
#                 elif price < 10000:
#                     labels.append("price_5k_10k")
#                 elif price < 50000:
#                     labels.append("price_10k_50k")
#                 elif price < 100000:
#                     labels.append("price_50k_100k")
#                 else:
#                     labels.append("price_over_100k")
                
#                 # Add availability label
#                 if product.available:
#                     labels.append("in_stock")
#                 else:
#                     labels.append("out_of_stock")
                
#                 # Get timestamp in ISO format
#                 timestamp = datetime.now().isoformat()
#                 if hasattr(product, 'created') and product.created:
#                     timestamp = product.created.isoformat()
                
#                 # Create item data for Gorse with proper capitalization
#                 item_data = {
#                     'ItemId': product.gorse_item_id,
#                     'Categories': [product.category.name],
#                     'Labels': labels,
#                     'Timestamp': timestamp,
#                     'Comment': product.name,
#                     'IsHidden': not product.available
#                 }
                
#                 # Insert or update item in Gorse
#                 success = gorse_client.insert_item(item_data)
#                 if success:
#                     self.stdout.write(f'Synced product: {product.name}')
#                 else:
#                     self.stdout.write(self.style.WARNING(f'Failed to sync product: {product.name}'))
                
#             except Exception as e:
#                 self.stdout.write(self.style.ERROR(f'Error syncing product {product.id}: {str(e)}'))
        
#         self.stdout.write(self.style.SUCCESS('Product sync completed!'))

# class GorseClient:
#     def __init__(self):
#         self.base_url = settings.GORSE_API_URL
#         self.api_key = settings.GORSE_API_KEY
#         self.headers = {'Content-Type': 'application/json'}
#         if self.api_key:
#             self.headers['X-API-Key'] = self.api_key
    
#     def insert_item(self, item_data):
#         """
#         Insert or update an item in Gorse
#         """
#         url = f"{self.base_url}/api/item"
#         try:
#             response = requests.post(url, json=item_data, headers=self.headers)
#             response.raise_for_status()
#             return True
#         except Exception as e:
#             print(f"Error inserting item: {e}")
#             return False



import json
import os
import requests
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import Product


class Command(BaseCommand):
    help = 'Synchronize products with Gorse recommender system'

    def handle(self, *args, **options):
        if not settings.GORSE_API_URL:
            self.stdout.write(self.style.ERROR('GORSE_API_URL is not set in settings'))
            return

        gorse_client = GorseClient()

        # Get all products
        products = Product.objects.all()
        self.stdout.write(f'Syncing {products.count()} products with Gorse')

        for product in products:
            try:
                # Build categories list: main category and any sub-categories
                categories = []
                if product.category:
                    categories.append(product.category.name)
                if product.complete_category:
                    subcats = [c.strip() for c in product.complete_category.split(',') if c.strip()]
                    categories.extend(subcats)
                # Deduplicate
                categories = list(dict.fromkeys(categories))

                # Build labels: brand, vendor, and key terms from title
                labels = []
                if product.brand:
                    labels.append(product.brand.name)
                if product.vendor_name:
                    labels.append(product.vendor_name)
                # Split title by words longer than 3 chars
                title_terms = [t.strip('.,') for t in product.name.split() if len(t) > 3]
                labels.extend(title_terms)
                # Deduplicate
                labels = list(dict.fromkeys(labels))

                # Timestamp: use updated time, fallback to created
                timestamp = (product.updated or product.created).isoformat()

                # Comment: human-readable summary
                comment = f"{product.name} at PKR {product.price:.2f}"

                # Hidden flag: hide if not available
                is_hidden = not product.available

                # Prepare payload for Gorse
                item_data = {
                    'ItemId': product.gorse_item_id,
                    'Categories': categories,
                    'Labels': labels,
                    'Timestamp': timestamp,
                    'Comment': comment,
                    'IsHidden': is_hidden
                }

                # Insert or update in Gorse
                success = gorse_client.insert_item(item_data)
                if success:
                    self.stdout.write(f'Synced product: {product.name}')
                else:
                    self.stdout.write(self.style.WARNING(f'Failed to sync product: {product.name}'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error syncing product {product.id}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Product sync completed!'))


class GorseClient:
    def __init__(self):
        self.base_url = settings.GORSE_API_URL.rstrip('/')
        self.api_key = getattr(settings, 'GORSE_API_KEY', None)
        self.headers = {'Content-Type': 'application/json'}
        if self.api_key:
            self.headers['X-API-Key'] = self.api_key

    def insert_item(self, item_data):
        '''Insert or update an item in Gorse'''
        url = f"{self.base_url}/api/item"
        try:
            response = requests.post(url, json=item_data, headers=self.headers)
            response.raise_for_status()
    
            return True
        except Exception as e:
            print(f"Error inserting item {item_data['ItemId']}: {e}")
            return False