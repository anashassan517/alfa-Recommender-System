import json
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Category, Product, Brand
from django.core.files.base import ContentFile
import requests
from decimal import Decimal
import re

class Command(BaseCommand):
    help = 'Import products from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the updated JSON file')

    def handle(self, *args, **options):
        json_file_path = options['json_file']
        
        if not os.path.exists(json_file_path):
            self.stderr.write(self.style.ERROR(f'File not found: {json_file_path}'))
            return
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
        
        self.stdout.write(self.style.SUCCESS(f'Loaded {len(products_data)} products from JSON'))

        categories_cache = {}
        brands_cache = {}

        for item in products_data:
            try:
                # Unique ID: use SKU
                product_id = item['sku']
                # Name & slug from title/handle
                product_name = item['title']
                product_slug = item.get('handle') or slugify(product_name)

                # Prices
                discounted_price = Decimal(item['discounted_price'])
                original_price   = Decimal(item['original_price'])

                # Inventory
                # inventory_qty = item.get('inventory_quantity', 0)

                # Category: take the first of comma‐separated list
                cats = [c.strip() for c in item.get('category_names', '').split(',') if c.strip()]
                if cats:
                    cat_name = cats[0]
                else:
                    cat_name = "Uncategorized"

                cat_slug = slugify(cat_name)
                if cat_slug not in categories_cache:
                    category_obj, created = Category.objects.get_or_create(
                        slug=cat_slug,
                        defaults={'name': cat_name}
                    )
                    categories_cache[cat_slug] = category_obj
                    if created:
                        self.stdout.write(f'Created category: {cat_name}')
                category = categories_cache[cat_slug]

                # Brand: use brand_name
                brand = None
                brand_name = item.get('brand_name')
                if brand_name:
                    brand_slug = slugify(brand_name)
                    if brand_slug not in brands_cache:
                        brand_obj, created = Brand.objects.get_or_create(
                            slug=brand_slug,
                            defaults={'name': brand_name}
                        )
                        brands_cache[brand_slug] = brand_obj
                        if created:
                            self.stdout.write(f'Created brand: {brand_name}')
                        brand = brand_obj
                    else:
                        brand = brands_cache[brand_slug]

                # Create or update product
                product, created = Product.objects.update_or_create(
                    gorse_item_id=product_id,
                    defaults={
                        'name': product_name,
                        'slug': product_slug,
                        'price': discounted_price,
                        'original_price': original_price,
                        # 'inventory_quantity': inventory_qty,
                        'category': category,
                        'brand': brand,
                        # 'available': inventory_qty > 0,
                    }
                )
                if created:
                    self.stdout.write(f'Created product: {product_name}')
                else:
                    self.stdout.write(f'Updated product: {product_name}')

                # Images: download the first (only) link
                img_url = item.get('image_links')
                if img_url:
                    try:
                        resp = requests.get(img_url)
                        if resp.status_code == 200:
                            fname = os.path.basename(img_url)
                            product.image.save(
                                fname,
                                ContentFile(resp.content),
                                save=True
                            )
                            self.stdout.write(f'Downloaded image for {product_name}')
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Failed to download image for {product_name}: {e}'))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error processing SKU {item.get("sku")}: {e}'))

        self.stdout.write(self.style.SUCCESS('Product import completed!'))
