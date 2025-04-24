from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Category
from .forms import ProductForm, CategoryForm


def home_view(request):
    category_id = request.GET.get('category')
    
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'products/home.html', context)

@login_required
def product_management(request, product_id=None):
    """
    Управление товарами: создание, редактирование, удаление
    """
    products = Product.objects.all().select_related('category')
    categories = Category.objects.all()
    product = None
    
    if product_id:
        product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Обработка удаления
        if 'delete' in request.POST and product:
            product_name = product.name
            product.delete()
            messages.success(request, f'Товар "{product_name}" успешно удалён!')
            return redirect('product_management')
        
        # Обработка формы
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            action = "отредактирован" if product_id else "добавлен"
            messages.success(request, f'Товар "{product.name}" успешно {action}!')
            return redirect('product_management')
        else:
            # Вывод ошибок формы
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Ошибка в поле "{field}": {error}')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/add_product.html', {
        'products': products,
        'categories': categories,
        'product_form': form,
        'current_product': product,
        'active_tab': 'products',
        'show_products_section': True
    })

@login_required
def category_management(request, category_id=None):
    """
    Управление категориями: создание, редактирование, удаление
    """
    categories = Category.objects.all()
    category = None
    
    if category_id:
        category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        # Обработка удаления
        if 'delete' in request.POST and category:
            if category.product_set.exists():
                messages.error(request, 'Нельзя удалить категорию с товарами!')
            else:
                category_name = category.name
                category.delete()
                messages.success(request, f'Категория "{category_name}" успешно удалена!')
            return redirect('category_management')
        
        # Обработка формы
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            action = "отредактирована" if category_id else "добавлена"
            messages.success(request, f'Категория "{category.name}" успешно {action}!')
            return redirect('category_management')
        else:
            # Вывод ошибок формы
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Ошибка в поле "{field}": {error}')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'products/add_product.html', {
        'categories': categories,
        'category_form': form,
        'current_category': category,
        'active_tab': 'categories',
        'show_categories_section': True
    })