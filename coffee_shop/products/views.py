from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Product, Category
from .forms import ProductForm 

def home_view(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'products/home.html', context)

def product_detail_view(request, product_id):
    product = Product.objects.get(id=product_id, available=True)
    return render(request, 'products/product_detail.html', {'product': product})

@login_required
@user_passes_test(lambda u: u.is_staff)  # Только для персонала
def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductForm()
    
    return render(request, 'products/add_product.html', {'form': form})