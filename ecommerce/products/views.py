# products/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category
from .forms import ProductForm

from django.shortcuts import render
from .models import Product, Category
from django.conf import settings



def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})


def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form})


def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form})


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'products/product_confirm_delete.html', {'product': product})


# products/views.py

def home(request):
    # Fetch all products
    products = Product.objects.all()

    # Fetch all categories (optional, if you want to display categories as well)
    categories = Category.objects.all()

    return render(request, 'home.html', {
        'products': products,  # Pass products to the template
        'categories': categories,  # Optional: Pass categories to the template
    })