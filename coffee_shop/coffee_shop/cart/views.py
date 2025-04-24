from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Cart, CartItem, Order, OrderItem
import uuid
from datetime import datetime


@login_required
def view_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product')  
        total_price = sum(item.total_price for item in cart_items)
    except Cart.DoesNotExist:
        cart_items = []
        total_price = 0
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart/cart.html', context)

@login_required
def checkout(request):
    try:
        cart = request.user.cart
        
        if request.method == 'POST':
            # Валидация данных
            address = request.POST.get('address')
            phone = request.POST.get('phone')
            
            if not address or not phone:
                messages.error(request, 'Пожалуйста, заполните все обязательные поля')
                return redirect('cart:checkout')
            
            # Генерация номера заказа только при подтверждении
            order_number = f"FOX-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            
            # Создание заказа
            order = Order.objects.create(
                user=request.user,
                order_number=order_number,
                total_price=cart.total_price,
                address=address,
                phone=phone,
                comments=request.POST.get('comments', '')
            )
            
            # Перенос товаров в заказ
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            
            # Очистка корзины
            cart.items.all().delete()
            
            # Перенаправляем на страницу подтверждения
            return redirect('cart:order_confirmation', order_number=order.order_number)
            
        else:
            # GET запрос - просто отображаем форму
            cart_items = cart.items.select_related('product')
            
            if not cart_items:
                messages.warning(request, 'Ваша корзина пуста')
                return redirect('cart:view_cart')
            
            context = {
                'cart_items': cart_items,
                'total_price': cart.total_price,
            }
            return render(request, 'cart/checkout.html', context)
    
    except Cart.DoesNotExist:
        messages.error(request, 'Корзина не найдена')
        return redirect('cart:view_cart')

@login_required
def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'cart/order_confirmation.html', {'order': order})

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        try:
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
            
            messages.success(request, f'Товар "{product.name}" добавлен в корзину')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Товар "{product.name}" добавлен в корзину',
                    'cart_count': cart.items.count()  # Используем items вместо cartitem_set
                })
            
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
            messages.error(request, 'Ошибка при добавлении в корзину')
            return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    return redirect('home')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'Товар "{product_name}" удален из корзины')
    return redirect('cart:view_cart')

@login_required
def update_quantity(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Количество обновлено')
        else:
            cart_item.delete()
            messages.success(request, 'Товар удален из корзины')
    
    return redirect('cart:view_cart')

@login_required
def clear_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    messages.success(request, 'Корзина очищена')
    return redirect('cart:view_cart')

@login_required
def get_cart_count(request):
    cart = Cart.objects.get(user=request.user)
    count = cart.items.count()
    return JsonResponse({'count': count})