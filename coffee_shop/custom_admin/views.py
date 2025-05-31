from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from users.models import CustomUser
from django.contrib.auth.models import User
from django.contrib import messages
from cart.models import Order
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Доступ запрещен")
        return view_func(request, *args, **kwargs)
    return wrapper

@admin_required
def superuser_required(view_func):
    """Декоратор для проверки суперпользователя"""
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url='/login/',
        redirect_field_name=None
    )
    return actual_decorator(view_func)

@admin_required
def admin_panel(request):
    # Расчет выручки только для завершенных заказов
    revenue = Order.objects.filter(status='completed').aggregate(
        total_revenue=Sum('total_price')
    )['total_revenue'] or 0

    stats = {
        'users_count': CustomUser.objects.count(),
        'orders_count': Order.objects.count(),
        'revenue': revenue
    }
    return render(request, 'custom_admin/admin_panel.html', stats)

@admin_required
def user_list(request):
    search_query = request.GET.get('q', '')
    
    users = CustomUser.objects.all().order_by('-date_joined')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'custom_admin/user_list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@admin_required
def order_history(request):
    status = request.GET.get('status')
    search_query = request.GET.get('q', '')
    
    orders = Order.objects.select_related('user').prefetch_related('items').all()
    
    # Фильтрация по статусу
    if status:
        orders = orders.filter(status=status)
    
    # Поиск по номеру заказа или имени пользователя
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Получаем все возможные статусы для фильтров
    status_choices = Order.ORDER_STATUS
    
    paginator = Paginator(orders.order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'custom_admin/order_history.html', {
        'page_obj': page_obj,
        'status_choices': status_choices
    })

@admin_required
def order_detail(request, order_id):
    order = Order.objects.select_related('user').prefetch_related('items').get(id=order_id)
    return render(request, 'custom_admin/order_detail.html', {'order': order})

@admin_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        admin_comment = request.POST.get('admin_comment', '')
        
        # Проверяем, изменился ли статус
        if order.status != new_status:
            order.status = new_status
            messages.success(request, f'Статус заказа #{order.order_number} изменен на "{dict(order.ORDER_STATUS).get(new_status)}"')
        else:
            messages.info(request, 'Статус заказа не был изменен')
        
        # Обновляем комментарий администратора
        order.admin_comment = admin_comment
        order.save()
        
        return redirect('custom_admin:order_detail', order_id=order.id)
    
    return redirect('custom_admin:order_detail', order_id=order.id)