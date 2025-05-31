from users.models import CustomUser
from cart.models import Order

def admin_stats(request):
    if request.user.is_superuser:
        return {
            'users_count': CustomUser.objects.count(),
            'orders_count': Order.objects.count(),
            'total_revenue': sum(order.total_price for order in Order.objects.filter(status='completed'))
        }
    return {}