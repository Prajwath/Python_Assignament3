# cart/admin.py

from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'paid')
    list_filter = ('paid', 'created_at')
    inlines = [OrderItemInline]

admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)