from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.view_cart, name='view_cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:item_id>/', views.update_quantity, name='update_quantity'), 
    path('confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('checkout/', views.checkout, name='checkout'),
    path('clear/', views.clear_cart, name='clear_cart'),
]