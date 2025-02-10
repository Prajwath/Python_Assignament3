# products/admin.py

from django.contrib import admin
from .models import Product, Category

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category')
    list_filter = ('category',)
    search_fields = ('name',)

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)