from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('add/', views.add_product_view, name='add_product'),
    path('<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('add-category/', views.add_category_view, name='add_category'),
    path('api/', views.product_api, name='product_api'),
    path('api/<int:pk>/', views.product_detail_api, name='product_detail_api'),
    path('api/categories/', views.category_api, name='category_api'),
    path('api/categories/<int:pk>/', views.category_detail_api, name='category_detail_api'),
]