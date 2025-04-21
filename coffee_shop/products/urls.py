from django.urls import path
from . import views

urlpatterns = [
    # Главная страница
    path('', views.home_view, name='home'),
    
    # Управление товарами (все операции через один URL)
    path('products/', views.product_management, name='product_management'),
    path('products/<int:product_id>/', views.product_management, name='edit_product'),
    
    # Управление категориями
    path('categories/', views.category_management, name='category_management'),
    path('categories/<int:category_id>/', views.category_management, name='edit_category'),
]