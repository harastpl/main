from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import STLFile, PrintOrder
from .forms import STLUploadForm, PrintOrderForm
from .utils import process_stl_file_async, get_file_info
from cart.utils import get_or_create_cart
import os


def stl_upload(request):
    """Upload STL file"""
    if request.method == 'POST':
        form = STLUploadForm(request.POST, request.FILES)
        if form.is_valid():
            stl_file = form.save(commit=False)
            
            # Set user or session
            if request.user.is_authenticated:
                stl_file.user = request.user
            else:
                if not request.session.session_key:
                    request.session.create()
                stl_file.session_key = request.session.session_key
            
            # Get file size
            stl_file.file_size = stl_file.stl_file.size
            stl_file.save()
            
            # Start processing (in background)
            try:
                process_stl_file_async(stl_file.id)
                messages.success(
                    request, 
                    f'STL file "{stl_file.name}" uploaded successfully! Processing will begin shortly.'
                )
            except Exception as e:
                messages.warning(
                    request,
                    f'File uploaded but processing failed to start: {str(e)}'
                )
            
            return redirect('stl_uploads:detail', pk=stl_file.pk)
    else:
        form = STLUploadForm()
    
    return render(request, 'stl_uploads/upload.html', {'form': form})


def stl_list(request):
    """List STL files for current user/session"""
    if request.user.is_authenticated:
        stl_files = STLFile.objects.filter(user=request.user)
    else:
        if not request.session.session_key:
            stl_files = STLFile.objects.none()
        else:
            stl_files = STLFile.objects.filter(session_key=request.session.session_key)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        stl_files = stl_files.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        stl_files = stl_files.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(stl_files, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get status choices for filter
    status_choices = STLFile.STATUS_CHOICES
    
    context = {
        'page_obj': page_obj,
        'stl_files': page_obj,
        'query': query,
        'status_filter': status_filter,
        'status_choices': status_choices,
    }
    return render(request, 'stl_uploads/list.html', context)


def stl_detail(request, pk):
    """STL file detail view"""
    stl_file = get_object_or_404(STLFile, pk=pk)
    
    # Check permissions
    if request.user.is_authenticated:
        if stl_file.user != request.user and not request.user.is_staff:
            raise Http404("STL file not found")
    else:
        if stl_file.session_key != request.session.session_key:
            raise Http404("STL file not found")
    
    # Get related print orders
    print_orders = PrintOrder.objects.filter(stl_file=stl_file).order_by('-created_at')
    
    context = {
        'stl_file': stl_file,
        'print_orders': print_orders,
    }
    return render(request, 'stl_uploads/detail.html', context)


def create_print_order(request, stl_pk):
    """Create a print order for an STL file"""
    stl_file = get_object_or_404(STLFile, pk=stl_pk)
    
    # Check if file is ready for printing
    if stl_file.status != 'processed' or not stl_file.approved_for_printing:
        messages.error(request, 'This STL file is not ready for printing yet.')
        return redirect('stl_uploads:detail', pk=stl_file.pk)
    
    if request.method == 'POST':
        form = PrintOrderForm(request.POST)
        if form.is_valid():
            print_order = form.save(commit=False)
            print_order.stl_file = stl_file
            
            if request.user.is_authenticated:
                print_order.user = request.user
            
            # Calculate total cost
            base_cost = stl_file.estimated_cost or 500  # Default ₹500 if no estimate
            print_order.total_cost = base_cost * print_order.quantity
            
            print_order.save()
            
            messages.success(
                request,
                f'Print order #{print_order.id} created successfully! We will contact you soon.'
            )
            return redirect('stl_uploads:detail', pk=stl_file.pk)
    else:
        # Pre-fill form if user is authenticated
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'customer_name': f"{request.user.first_name} {request.user.last_name}".strip(),
                'customer_email': request.user.email,
            }
        form = PrintOrderForm(initial=initial_data)
    
    context = {
        'form': form,
        'stl_file': stl_file,
    }
    return render(request, 'stl_uploads/create_order.html', context)


@require_POST
def delete_stl(request, pk):
    """Delete STL file"""
    stl_file = get_object_or_404(STLFile, pk=pk)
    
    # Check permissions
    if request.user.is_authenticated:
        if stl_file.user != request.user and not request.user.is_staff:
            raise Http404("STL file not found")
    else:
        if stl_file.session_key != request.session.session_key:
            raise Http404("STL file not found")
    
    # Check if there are pending print orders
    if stl_file.print_orders.filter(status__in=['pending', 'confirmed', 'printing']).exists():
        messages.error(request, 'Cannot delete STL file with active print orders.')
        return redirect('stl_uploads:detail', pk=stl_file.pk)
    
    file_name = stl_file.name
    stl_file.delete()
    
    messages.success(request, f'STL file "{file_name}" deleted successfully.')
    return redirect('stl_uploads:list')


def download_stl(request, pk):
    """Download STL file"""
    stl_file = get_object_or_404(STLFile, pk=pk)
    
    # Check permissions
    if request.user.is_authenticated:
        if stl_file.user != request.user and not request.user.is_staff:
            raise Http404("STL file not found")
    else:
        if stl_file.session_key != request.session.session_key:
            raise Http404("STL file not found")
    
    if not stl_file.stl_file or not os.path.exists(stl_file.stl_file.path):
        raise Http404("STL file not found on disk")
    
    with open(stl_file.stl_file.path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{stl_file.name}.stl"'
        return response


def preview_image(request, pk):
    """Serve STL preview image"""
    stl_file = get_object_or_404(STLFile, pk=pk)
    
    if not stl_file.preview_image:
        raise Http404("Preview image not found")
    
    with open(stl_file.preview_image.path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='image/png')
        return response


@require_POST
def reprocess_stl(request, pk):
    """Reprocess STL file"""
    stl_file = get_object_or_404(STLFile, pk=pk)
    
    # Check permissions
    if request.user.is_authenticated:
        if stl_file.user != request.user and not request.user.is_staff:
            raise Http404("STL file not found")
    else:
        if stl_file.session_key != request.session.session_key:
            raise Http404("STL file not found")
    
    if not stl_file.can_be_processed:
        messages.error(request, 'This file cannot be reprocessed in its current state.')
        return redirect('stl_uploads:detail', pk=stl_file.pk)
    
    try:
        process_stl_file_async(stl_file.id)
        messages.success(request, 'Reprocessing started. Check back in a few minutes.')
    except Exception as e:
        messages.error(request, f'Error starting reprocessing: {str(e)}')
    
    return redirect('stl_uploads:detail', pk=stl_file.pk)


def check_processing_status(request, pk):
    """AJAX endpoint to check processing status"""
    stl_file = get_object_or_404(STLFile, pk=pk)
    
    # Check permissions
    if request.user.is_authenticated:
        if stl_file.user != request.user and not request.user.is_staff:
            raise Http404("STL file not found")
    else:
        if stl_file.session_key != request.session.session_key:
            raise Http404("STL file not found")
    
    return JsonResponse({
        'status': stl_file.status,
        'status_display': stl_file.get_status_display(),
        'estimated_print_time': stl_file.estimated_print_time,
        'estimated_cost': float(stl_file.estimated_cost) if stl_file.estimated_cost else None,
        'has_preview': bool(stl_file.preview_image),
        'approved_for_printing': stl_file.approved_for_printing,
    })