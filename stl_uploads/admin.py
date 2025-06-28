from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, Http404
from .models import STLFile, PrintOrder
from .utils import process_stl_file_async
import os


@admin.register(STLFile)
class STLFileAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user_info', 'status_badge', 'file_size_mb', 
        'print_quality', 'created_at', 'action_buttons'
    ]
    list_filter = ['status', 'print_quality', 'approved_for_printing', 'created_at']
    search_fields = ['name', 'user__username', 'user__email']
    readonly_fields = [
        'file_size', 'created_at', 'updated_at', 'processed_at',
        'estimated_print_time', 'estimated_material_usage', 'estimated_cost'
    ]
    
    fieldsets = (
        ('File Information', {
            'fields': ('name', 'description', 'stl_file', 'file_size', 'user', 'session_key')
        }),
        ('Print Settings', {
            'fields': ('print_quality', 'infill_percentage', 'supports_needed')
        }),
        ('Processing Status', {
            'fields': ('status', 'processing_log', 'processed_at')
        }),
        ('Estimates', {
            'fields': ('estimated_print_time', 'estimated_material_usage', 'estimated_cost')
        }),
        ('Preview & Output', {
            'fields': ('preview_image', 'gcode_file')
        }),
        ('Admin Controls', {
            'fields': ('approved_for_printing', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:stl_id>/process/', self.admin_site.admin_view(self.process_stl), name='process_stl'),
            path('<int:stl_id>/download/', self.admin_site.admin_view(self.download_stl), name='download_stl'),
            path('<int:stl_id>/download-gcode/', self.admin_site.admin_view(self.download_gcode), name='download_gcode'),
            path('<int:stl_id>/preview/', self.admin_site.admin_view(self.view_preview), name='view_preview'),
        ]
        return custom_urls + urls

    def user_info(self, obj):
        if obj.user:
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                obj.user.username,
                obj.user.email
            )
        return format_html('<em>Anonymous</em><br><small>{}</small>', obj.session_key or 'No session')
    user_info.short_description = 'User'

    def status_badge(self, obj):
        color = obj.get_status_color()
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def action_buttons(self, obj):
        buttons = []
        
        # Process button
        if obj.can_be_processed:
            process_url = reverse('admin:process_stl', args=[obj.id])
            buttons.append(f'<a href="{process_url}" class="btn btn-sm btn-warning">Process</a>')
        
        # Download STL button
        download_url = reverse('admin:download_stl', args=[obj.id])
        buttons.append(f'<a href="{download_url}" class="btn btn-sm btn-primary">Download STL</a>')
        
        # Download G-code button (if available)
        if obj.gcode_file:
            gcode_url = reverse('admin:download_gcode', args=[obj.id])
            buttons.append(f'<a href="{gcode_url}" class="btn btn-sm btn-success">Download G-code</a>')
        
        # Preview button (if available)
        if obj.preview_image:
            preview_url = reverse('admin:view_preview', args=[obj.id])
            buttons.append(f'<a href="{preview_url}" class="btn btn-sm btn-info" target="_blank">Preview</a>')
        
        return format_html(' '.join(buttons))
    action_buttons.short_description = 'Actions'

    def process_stl(self, request, stl_id):
        """Process STL file with OrcaSlicer"""
        stl_file = get_object_or_404(STLFile, id=stl_id)
        
        if not stl_file.can_be_processed:
            messages.error(request, f'File "{stl_file.name}" cannot be processed in its current state.')
            return redirect('admin:stl_uploads_stlfile_changelist')
        
        try:
            # Process the file (in a real application, this should be done asynchronously)
            process_stl_file_async(stl_file.id)
            messages.success(request, f'Processing started for "{stl_file.name}". Check back in a few minutes.')
        except Exception as e:
            messages.error(request, f'Error starting processing: {str(e)}')
        
        return redirect('admin:stl_uploads_stlfile_changelist')

    def download_stl(self, request, stl_id):
        """Download STL file"""
        stl_file = get_object_or_404(STLFile, id=stl_id)
        
        if not stl_file.stl_file or not os.path.exists(stl_file.stl_file.path):
            raise Http404("STL file not found")
        
        with open(stl_file.stl_file.path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{stl_file.name}.stl"'
            return response

    def download_gcode(self, request, stl_id):
        """Download G-code file"""
        stl_file = get_object_or_404(STLFile, id=stl_id)
        
        if not stl_file.gcode_file or not os.path.exists(stl_file.gcode_file.path):
            raise Http404("G-code file not found")
        
        with open(stl_file.gcode_file.path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{stl_file.name}.gcode"'
            return response

    def view_preview(self, request, stl_id):
        """View STL preview image"""
        stl_file = get_object_or_404(STLFile, id=stl_id)
        
        if not stl_file.preview_image:
            raise Http404("Preview image not found")
        
        with open(stl_file.preview_image.path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='image/png')
            return response


@admin.register(PrintOrder)
class PrintOrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'stl_file_name', 'customer_name', 'quantity', 
        'total_cost', 'status_badge', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'stl_file__name']
    readonly_fields = ['created_at', 'updated_at', 'total_estimated_time']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('stl_file', 'quantity', 'total_cost', 'status')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'delivery_address')
        }),
        ('Timeline', {
            'fields': ('created_at', 'updated_at', 'estimated_completion', 'total_estimated_time')
        }),
        ('Admin Notes', {
            'fields': ('admin_notes',)
        })
    )

    def stl_file_name(self, obj):
        return obj.stl_file.name
    stl_file_name.short_description = 'STL File'

    def status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'confirmed': 'info',
            'printing': 'primary',
            'completed': 'success',
            'cancelled': 'danger',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


# Custom admin site styling
admin.site.site_header = "Volt3dge STL Management"
admin.site.site_title = "STL Admin"
admin.site.index_title = "STL File Management Dashboard"