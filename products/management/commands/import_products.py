
# import json
# import os
# from django.core.management.base import BaseCommand
# from django.utils.text import slugify
# from products.models import Category, Product, Brand
# from django.core.files.base import ContentFile
# import requests
# from decimal import Decimal
# import re

# class Command(BaseCommand):
#     help = 'Import products from JSON file'

#     def add_arguments(self, parser):
#         parser.add_argument('json_file', type=str, help='Path to the JSON file')

#     def handle(self, *args, **options):
#         json_file_path = options['json_file']
        
#         if not os.path.exists(json_file_path):
#             self.stdout.write(self.style.ERROR(f'File not found: {json_file_path}'))
#             return
        
#         with open(json_file_path, 'r', encoding='utf-8') as file:
#             products_data = json.load(file)
        
#         self.stdout.write(self.style.SUCCESS(f'Loaded {len(products_data)} products from JSON'))
        
#         categories_cache = {}
#         brands_cache = {}
        
#         for item in products_data:
#             try:
#                 # Process product data
#                 product_id = item['id']
#                 product_name = item['title']
#                 product_slug = slugify(product_name)
                
#                 # Process price - remove commas and convert to Decimal
#                 discounted_price_str = item['variant_detail']['discounted_price']
#                 discounted_price_clean = re.sub(r'[^\d.]', '', discounted_price_str)
#                 discounted_price = Decimal(discounted_price_clean)
                
#                 original_price_str = item['variant_detail']['original_price']
#                 original_price_clean = re.sub(r'[^\d.]', '', original_price_str)
#                 original_price = Decimal(original_price_clean)
                
#                 # Get product description (use empty string if not available)
#                 product_description = ""
#                 if 'features' in item and item['features']:
#                     product_description = '\n'.join(item['features'])
                
#                 # Process delivery date and other fields
#                 delivery_date = item.get('delivery_date', '')
#                 free_shipping = item.get('free_shipping', False)
#                 loyalty_points = item.get('loyalty_points', 0)
                
#                 # Get the first category or create a default one
#                 if item['category']:
#                     category_name = item['category'][0]['title']
#                     category_slug = slugify(category_name)
                    
#                     if category_slug not in categories_cache:
#                         category, created = Category.objects.get_or_create(
#                             slug=category_slug,
#                             defaults={'name': category_name}
#                         )
#                         categories_cache[category_slug] = category
#                         if created:
#                             self.stdout.write(f'Created category: {category_name}')
                    
#                     category = categories_cache[category_slug]
#                 else:
#                     # Create or get a default category if none exists
#                     default_category_name = "Uncategorized"
#                     default_category_slug = slugify(default_category_name)
                    
#                     if default_category_slug not in categories_cache:
#                         category, created = Category.objects.get_or_create(
#                             slug=default_category_slug,
#                             defaults={'name': default_category_name}
#                         )
#                         categories_cache[default_category_slug] = category
                    
#                     category = categories_cache[default_category_slug]
                
#                 # Process brand
#                 brand = None
#                 if item.get('brand'):
#                     brand_name = item['brand'][0]['title']
#                     brand_slug = slugify(brand_name)
                    
#                     if brand_slug not in brands_cache:
#                         brand, created = Brand.objects.get_or_create(
#                             slug=brand_slug,
#                             defaults={'name': brand_name}
#                         )
#                         brands_cache[brand_slug] = brand
#                         if created:
#                             self.stdout.write(f'Created brand: {brand_name}')
                            
#                             # Download brand logo if available
#                             brand_logo_url = item['brand'][0].get('logo_image')
#                             if brand_logo_url:
#                                 try:
#                                     response = requests.get(brand_logo_url)
#                                     if response.status_code == 200:
#                                         file_name = os.path.basename(brand_logo_url)
#                                         brand.logo.save(
#                                             file_name,
#                                             ContentFile(response.content),
#                                             save=True
#                                         )
#                                 except Exception as e:
#                                     self.stdout.write(self.style.WARNING(f'Failed to download brand logo: {str(e)}'))
                    
#                     brand = brands_cache[brand_slug]
                
#                 # Check if product already exists
#                 product, created = Product.objects.get_or_create(
#                     gorse_item_id=product_id,
#                     defaults={
#                         'name': product_name,
#                         'slug': product_slug,
#                         'price': discounted_price,
#                         'original_price': original_price,
#                         'description': product_description,
#                         'category': category,
#                         'brand': brand,
#                         'available': not item.get('sold_out', False),
#                         'delivery_date': delivery_date,
#                         'free_shipping': free_shipping,
#                         'loyalty_points': loyalty_points
#                     }
#                 )
                
#                 if created:
#                     # If there are images, download the first one
#                     if item.get('images') and len(item['images']) > 0:
#                         image_url = item['images'][0]
#                         try:
#                             response = requests.get(image_url)
#                             if response.status_code == 200:
#                                 # Get the file name from the URL
#                                 file_name = os.path.basename(image_url)
#                                 product.image.save(
#                                     file_name,
#                                     ContentFile(response.content),
#                                     save=True
#                                 )
#                                 self.stdout.write(f'Downloaded image for: {product_name}')
#                         except Exception as e:
#                             self.stdout.write(self.style.WARNING(f'Failed to download image for {product_name}: {str(e)}'))
                    
#                     self.stdout.write(f'Created product: {product_name}')
#                 else:
#                     self.stdout.write(f'Product already exists: {product_name}')
            
#             except Exception as e:
#                 self.stdout.write(self.style.ERROR(f'Error processing product {item.get("id", "unknown")}: {str(e)}'))
        
#         self.stdout.write(self.style.SUCCESS('Product import completed!'))

import json
import os
import requests
import re
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files.base import ContentFile
from products.models import Category, Product, Brand


class Command(BaseCommand):
    help = 'Import products from cleaned JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **options):
        json_file_path = options['json_file']
        
        if not os.path.exists(json_file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {json_file_path}'))
            return
        
        with open(json_file_path, 'r', encoding='utf-8') as file:
            products_data = json.load(file)
        
        self.stdout.write(self.style.SUCCESS(f'Loaded {len(products_data)} products from JSON'))
        
        categories_cache = {}
        brands_cache = {}

        for item in products_data:
            try:
                product_id = item['sku']  # Use SKU as ID
                product_name = item['title']
                product_slug = slugify(product_name)

                discounted_price = Decimal(str(item.get('discounted_price', 0)))
                original_price = Decimal(str(item.get('original_price', 0)))

                # Handle main category
                main_category_name = item.get('main_category', 'Uncategorized').strip()
                main_category_slug = slugify(main_category_name)

                if main_category_slug not in categories_cache:
                    category, created = Category.objects.get_or_create(
                        slug=main_category_slug,
                        defaults={'name': main_category_name}
                    )
                    categories_cache[main_category_slug] = category
                    if created:
                        self.stdout.write(f'Created category: {main_category_name}')
                category = categories_cache[main_category_slug]

                # Handle brand
                brand = None
                brand_name = item.get('brand_name', '').strip()
                if brand_name:
                    brand_slug = slugify(brand_name)
                    if brand_slug not in brands_cache:
                        brand, created = Brand.objects.get_or_create(
                            slug=brand_slug,
                            defaults={'name': brand_name}
                        )
                        brands_cache[brand_slug] = brand
                        if created:
                            self.stdout.write(f'Created brand: {brand_name}')
                    brand = brands_cache[brand_slug]
                
                #vendor_name
                vendor_name = item.get('vendor_name', '').strip()

                #add sub category from category_names
                complete_category = item.get('category_names', '').strip()


                # Check if product already exists
                product, created = Product.objects.get_or_create(
                    gorse_item_id=product_id,
                    defaults={
                        'name': product_name,
                        'slug': product_slug,
                        'price': discounted_price,
                        'original_price': original_price,
                        'category': category,
                        'brand': brand,
                        'available': item.get('inventory_quantity', 0) > 0,
                        'vendor_name': vendor_name,
                        'complete_category': complete_category,
                    }
                )

                if created:
                    # Handle images
                    image_links = item.get('image_links', '')
                    if image_links:
                        first_image_url = image_links.split(',')[0].strip()
                        if first_image_url:
                            try:
                                response = requests.get(first_image_url)
                                if response.status_code == 200:
                                    file_name = os.path.basename(first_image_url)
                                    product.image.save(
                                        file_name,
                                        ContentFile(response.content),
                                        save=True
                                    )
                                    self.stdout.write(f'Downloaded image for: {product_name}')
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f'Image download failed for {product_name}: {str(e)}'))

                    self.stdout.write(f'Created product: {product_name}')
                else:
                    self.stdout.write(f'Product already exists: {product_name}')
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing product {item.get("sku", "unknown")}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Product import completed!'))
