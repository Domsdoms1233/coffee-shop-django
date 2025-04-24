from .models import Cart

def get_cart_for_user(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart