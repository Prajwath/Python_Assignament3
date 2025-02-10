# cart/views.py
# import razorpay
from django.shortcuts import render, get_object_or_404, redirect
from .models import Cart, CartItem
from .models import Product
from .models import Order, OrderItem
# import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest

from rest_framework import generics
from .models import Cart, Order
from .serializers import CartSerializer, OrderSerializer


def get_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return cart


def cart_detail(request):
    cart = get_cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_detail')


def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart_detail')


def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('cart_detail')


def checkout(request):
    cart = get_cart(request)
    order = Order.objects.create(user=request.user)

    # Create Order Items
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            price=item.product.price,
            quantity=item.quantity
        )

    # Clear Cart
    cart.items.all().delete()

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create Razorpay order
    razorpay_order = client.order.create({
        'amount': int(order.get_total_cost() * 100),  # Amount in paise (100 = 1 INR)
        'currency': 'INR',
        'payment_capture': 1  # Auto capture payment
    })

    # Save Razorpay order ID to the Order model
    order.razorpay_order_id = razorpay_order['id']
    order.save()

    return render(request, 'cart/checkout.html', {
        'order': order,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': razorpay_order['amount']
    })


@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        # Get the payment details from the POST request
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Verify the payment signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            # Mark the order as paid
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.paid = True
            order.save()
            return render(request, 'cart/payment_success.html', {'order': order})
        except:
            return HttpResponseBadRequest("Invalid Payment Details")
    return HttpResponseBadRequest("Invalid Request")



class CartAPIView(generics.RetrieveAPIView):
    serializer_class = CartSerializer

    def get_object(self):
        return Cart.objects.get(user=self.request.user)

class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)