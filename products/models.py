# from django.db import models
# from django.urls import reverse

# class Category(models.Model):
#     name = models.CharField(max_length=100)
#     slug = models.SlugField(max_length=100, unique=True)
    
#     class Meta:
#         ordering = ('name',)
#         verbose_name_plural = 'categories'
    
#     def __str__(self):
#         return self.name
    
#     def get_absolute_url(self):
#         return reverse('products:category_list', args=[self.slug])

# class Product(models.Model):
#     category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
#     name = models.CharField(max_length=200)
#     slug = models.SlugField(max_length=200, unique=True)
#     image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
#     description = models.TextField(blank=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     available = models.BooleanField(default=True)
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#     # For gorse.io integration
#     gorse_item_id = models.CharField(max_length=100, unique=True)
    
#     class Meta:
#         ordering = ('name',)
#         index_together = (('id', 'slug'),)
    
#     def __str__(self):
#         return self.name
    
#     def get_absolute_url(self):
#         return reverse('products:product_detail', args=[self.id, self.slug])
from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    
    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:category_list', args=[self.slug])

class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True)
    
    class Meta:
        ordering = ('name',)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=False)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    delivery_date = models.CharField(max_length=100, blank=True)
    free_shipping = models.BooleanField(default=False)
    loyalty_points = models.IntegerField(default=0)
    # For gorse.io integration
    gorse_item_id = models.CharField(max_length=100, unique=True)
    
    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.id, self.slug])