from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('add-product/', views.add_product_view, name='add_product'),
]