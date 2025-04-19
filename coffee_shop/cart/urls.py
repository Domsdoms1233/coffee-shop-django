from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('update/<int:item_id>/', views.update_quantity_view, name='update_quantity'),
]