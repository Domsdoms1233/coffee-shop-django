from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Product, Category
from .forms import ProductForm

@login_required
def product_management(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'products/add_product.html', {
        'products': products,
        'categories': categories
    })

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_management')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/add_product.html', {
        'product': product,
        'products': Product.objects.all(),
        'categories': categories,
        'form': form
    })

@login_required
@require_http_methods(["DELETE"])
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return JsonResponse({'success': True})

# API endpoints
@login_required
@require_http_methods(["GET", "POST"])
def product_api(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            return JsonResponse({
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'category': product.category.id,
                'description': product.description,
                'available': product.available,
                'image_url': product.image.url if product.image else ''
            })
        return JsonResponse({'errors': form.errors}, status=400)
    else:
        products = Product.objects.all()
        data = [{
            'id': p.id,
            'name': p.name,
            'price': str(p.price),
            'category': p.category.id,
            'description': p.description,
            'available': p.available,
            'image_url': p.image.url if p.image else ''
        } for p in products]
        return JsonResponse(data, safe=False)

@login_required
@require_http_methods(["GET", "PUT", "DELETE"])
def product_detail_api(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'PUT':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            return JsonResponse({
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'category': product.category.id,
                'description': product.description,
                'available': product.available,
                'image_url': product.image.url if product.image else ''
            })
        return JsonResponse({'errors': form.errors}, status=400)
    elif request.method == 'DELETE':
        product.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'category': product.category.id,
            'description': product.description,
            'available': product.available,
            'image_url': product.image.url if product.image else ''
        })

# Категории API
@login_required
@require_http_methods(["GET", "POST"])
def category_api(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            category = Category.objects.create(name=name)
            return JsonResponse({
                'id': category.id,
                'name': category.name
            })
        return JsonResponse({'error': 'Name is required'}, status=400)
    else:
        categories = Category.objects.all()
        data = [{
            'id': c.id,
            'name': c.name,
            'product_count': c.product_set.count()
        } for c in categories]
        return JsonResponse(data, safe=False)

@login_required
@require_http_methods(["GET", "PUT", "DELETE"])
def category_detail_api(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'PUT':
        name = request.POST.get('name')
        if name:
            category.name = name
            category.save()
            return JsonResponse({
                'id': category.id,
                'name': category.name
            })
        return JsonResponse({'error': 'Name is required'}, status=400)
    elif request.method == 'DELETE':
        if category.product_set.exists():
            return JsonResponse({
                'error': 'Cannot delete category with products'
            }, status=400)
        category.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({
            'id': category.id,
            'name': category.name,
            'product_count': category.product_set.count()
        })