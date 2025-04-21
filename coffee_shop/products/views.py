from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Category
from .forms import ProductForm, CategoryForm

def home_view(request):
    """Главная страница с фильтрацией по категориям"""
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    
    products = Product.objects.filter(available=True).select_related('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    return render(request, 'products/home.html', {
        'products': products,
        'categories': categories
    })

@login_required
def product_management(request, product_id=None):
    """
    Универсальный обработчик для:
    - Просмотра списка товаров
    - Добавления нового товара (когда product_id=None)
    - Редактирования существующего товара
    - Удаления товара
    """
    products = Product.objects.all()
    categories = Category.objects.all()
    product = None
    
    # Получаем товар для редактирования, если передан ID
    if product_id:
        product = get_object_or_404(Product, id=product_id)
    
    # Обработка POST-запроса (добавление/редактирование/удаление)
    if request.method == 'POST':
        # Обработка удаления
        if 'delete' in request.POST:
            if product:
                product.delete()
                messages.success(request, f'Товар "{product.name}" удален!')
                return redirect('product_management')
        
        # Обработка добавления/редактирования
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            action = "отредактирован" if product_id else "добавлен"
            messages.success(request, f'Товар "{product.name}" успешно {action}!')
            return redirect('product_management')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/add_product.html', {
        'products': products,
        'categories': categories,
        'form': form,
        'current_product': product
    })

@login_required
def category_management(request, category_id=None):
    """Управление категориями"""
    categories = Category.objects.all()
    category = None
    
    if category_id:
        category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        if 'delete' in request.POST and category:
            if category.product_set.exists():
                messages.error(request, 'Нельзя удалить категорию с товарами!')
            else:
                category.delete()
                messages.success(request, f'Категория "{category.name}" удалена!')
            return redirect('category_management')
        
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            action = "отредактирована" if category_id else "добавлена"
            messages.success(request, f'Категория "{category.name}" успешно {action}!')
            return redirect('category_management')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'products/categories.html', {
        'categories': categories,
        'form': form,
        'current_category': category
    })