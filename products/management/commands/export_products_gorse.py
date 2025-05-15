from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import Product
from recommendations.gorse_client import GorseClient
from datetime import datetime
import csv
import os

class Command(BaseCommand):
    help = 'Export products to CSV for Gorse and sync directly with Gorse API'

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, help='Output CSV file path')
        parser.add_argument('--direct', action='store_true', help='Sync directly with Gorse API')

    def handle(self, *args, **options):
        output_file = options.get('output')
        direct_sync = options.get('direct', False)
        
        products = Product.objects.all()
        count = products.count()
        
        self.stdout.write(f'Processing {count} products')
        
        # If direct sync is requested
        if direct_sync:
            self.sync_with_gorse_api(products)
            return
            
        # Otherwise export to CSV
        if not output_file:
            output_dir = os.path.join(settings.BASE_DIR, 'data')
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f'gorse_products_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        
        self.export_to_csv(products, output_file)
    
    def sync_with_gorse_api(self, products):
        gorse_client = GorseClient()
        success_count = 0
        
        for i, product in enumerate(products, 1):
            try:
                # Create labels list with all relevant product information
                labels = [product.category.name]
                
                # Add price range labels
                price = float(product.price)
                if price < 1000:
                    labels.append("price_under_1k")
                elif price < 5000:
                    labels.append("price_1k_5k")
                elif price < 10000:
                    labels.append("price_5k_10k")
                elif price < 50000:
                    labels.append("price_10k_50k")
                elif price < 100000:
                    labels.append("price_50k_100k")
                else:
                    labels.append("price_over_100k")
                
                # Add availability label
                if product.available:
                    labels.append("in_stock")
                else:
                    labels.append("out_of_stock")
                
                # Get timestamp in ISO format
                timestamp = datetime.now().isoformat()
                if hasattr(product, 'created') and product.created:
                    timestamp = product.created.isoformat()
                
                # Create item data for Gorse with proper capitalization
                item_data = {
                    'ItemId': product.gorse_item_id,
                    'Categories': [product.category.name],
                    'Labels': labels,
                    'Timestamp': timestamp,
                    'Comment': product.name,
                    'IsHidden': not product.available
                }
                
                # Insert or update item in Gorse
                success = gorse_client.insert_item(item_data)
                if success:
                    success_count += 1
                
                # Progress update
                if i % 10 == 0 or i == len(products):
                    self.stdout.write(f'Processed {i}/{len(products)} products, {success_count} successful')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error syncing product {product.id}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Product sync completed! {success_count}/{len(products)} successful'))
    
    def export_to_csv(self, products, output_file):
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['item_id', 'category', 'labels', 'timestamp', 'comment', 'is_hidden'])
            
            # Write products
            for product in products:
                # Create labels string
                labels = product.category.name
                
                # Add price range label
                price = float(product.price)
                if price < 1000:
                    labels += ",price_under_1k"
                elif price < 5000:
                    labels += ",price_1k_5k"
                elif price < 10000:
                    labels += ",price_5k_10k"
                elif price < 50000:
                    labels += ",price_10k_50k"
                elif price < 100000:
                    labels += ",price_50k_100k"
                else:
                    labels += ",price_over_100k"
                
                # Add availability label
                if product.available:
                    labels += ",in_stock"
                else:
                    labels += ",out_of_stock"
                
                # Get timestamp string
                timestamp = ""
                if hasattr(product, 'created') and product.created:
                    timestamp = product.created.isoformat()
                
                writer.writerow([
                    product.gorse_item_id,
                    product.category.name,
                    labels,
                    timestamp,
                    product.name,
                    not product.available
                ])
            
        self.stdout.write(self.style.SUCCESS(f'Exported {len(products)} products to {output_file}'))