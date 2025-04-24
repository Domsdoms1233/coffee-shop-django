from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from products.models import Product
from .models import Cart, CartItem

@login_required
def cart_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.all()  # Используем related_name='items' вместо cartitem_set
    
    context = {
        'cart': cart,
        'items': items,
        'total': cart.total_price,  # Используем свойство из модели
    }
    return render(request, 'cart/cart.html', context)

@login_required
def cart_count_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    count = cart.items.count()
    return JsonResponse({'count': count})

@login_required
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': cart.total_price,
            'cart_quantity': cart.total_quantity
        })
    
    return redirect('cart')

@login_required
def remove_from_cart_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart = cart_item.cart
    cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': cart.total_price,
            'cart_quantity': cart.total_quantity
        })
    
    return redirect('cart')

@login_required
def checkout_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.all()
    
    if not items:
        return redirect('cart')
    
    context = {
        'cart': cart,
        'items': items,
        'total': cart.total_price,
    }
    return render(request, 'cart/checkout.html', context)



@login_required
def update_quantity_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'item_price': str(cart_item.total_price),
            'cart_total': str(cart_item.cart.total_price),
            'cart_quantity': cart_item.cart.total_quantity
        })
    
    # Если это не AJAX-запрос, перенаправляем обратно в корзину
    return redirect('cart')