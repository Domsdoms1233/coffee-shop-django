from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
import uuid
from decimal import Decimal, getcontext

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product')
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart/cart.html', context)

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        return redirect('cart:view_cart')
    
    getcontext().prec = 6
    total_price = sum(Decimal(str(item.product.price)) * item.quantity for item in cart.items.all())
    max_foxcoins = min(request.user.foxcoins, int(total_price / Decimal('2')))
    
    if request.method == 'POST':
        try:
            # Обработка формы
            use_foxcoins = request.POST.get('use_foxcoins') == 'on'
            foxcoins_amount = int(request.POST.get('foxcoins_amount', 0))
            
            # Валидация Foxcoins
            if use_foxcoins:
                if foxcoins_amount <= 0:
                    raise ValueError("Введите положительное количество Foxcoins")
                if foxcoins_amount > max_foxcoins:
                    raise ValueError(f"Можно использовать не более {max_foxcoins} Foxcoins")
                if foxcoins_amount > request.user.foxcoins:
                    raise ValueError("Недостаточно Foxcoins на счету")
            
            # Расчет итоговой суммы
            final_price = float(total_price) - (foxcoins_amount if use_foxcoins else 0)
            
            # Создание заказа
            order = Order.objects.create(
                user=request.user,
                phone=request.POST.get('phone'),
                address=request.POST.get('address'),
                comments=request.POST.get('comments', ''),
                total_price=final_price,
                foxcoins_used=foxcoins_amount if use_foxcoins else 0,
                order_number=str(uuid.uuid4())[:8].upper()
            )
            
            # Добавление товаров в заказ
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=float(item.product.price),
                    quantity=item.quantity
                )
            
            # Обновление Foxcoins пользователя
            if use_foxcoins:
                request.user.foxcoins -= foxcoins_amount
            
            # Начисление бонусов (10% от суммы заказа)
            bonus = int(Decimal(str(final_price)) * Decimal('0.10'))
            request.user.foxcoins += bonus
            request.user.save()
            
            # Очистка корзины
            cart.items.all().delete()
            
            messages.success(request, f"Заказ оформлен! Начислено {bonus} Foxcoins")
            return redirect('cart:order_confirmation', order_number=order.order_number)
            
        except Exception as e:
            messages.error(request, f"Ошибка: {str(e)}")
            return redirect('cart:checkout')
    
    return render(request, 'cart/checkout.html', {
        'cart_items': cart.items.all(),
        'total_price': float(total_price),
        'max_foxcoins': max_foxcoins,
        'user_foxcoins': request.user.foxcoins
    })

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
                    'cart_count': cart.items.count()
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
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()
    messages.success(request, 'Корзина очищена')
    return redirect('cart:view_cart')

@login_required
def get_cart_count(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    count = cart.items.count()
    return JsonResponse({'count': count})