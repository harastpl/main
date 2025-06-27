from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category


def product_list(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'products': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'query': query,
    }
    return render(request, 'core/product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, available=True)
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(pk=product.pk)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'core/product_detail.html', context)


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'core/category_list.html', {'categories': categories})