import os
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


def stl_upload_path(instance, filename):
    """Generate upload path for STL files"""
    # Create path: stl_files/user_id/year/month/filename
    return f'stl_files/{instance.user.id if instance.user else "anonymous"}/{timezone.now().year}/{timezone.now().month}/{filename}'


class STLFile(models.Model):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('failed', 'Processing Failed'),
        ('ready', 'Ready for Print'),
    ]

    PRINT_QUALITY_CHOICES = [
        ('draft', 'Draft (0.3mm)'),
        ('normal', 'Normal (0.2mm)'),
        ('fine', 'Fine (0.15mm)'),
        ('ultra_fine', 'Ultra Fine (0.1mm)'),
    ]

    INFILL_CHOICES = [
        ('10', '10%'),
        ('15', '15%'),
        ('20', '20%'),
        ('25', '25%'),
        ('50', '50%'),
        ('75', '75%'),
        ('100', '100%'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    
    # File information
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    stl_file = models.FileField(upload_to=stl_upload_path)
    file_size = models.BigIntegerField(help_text="File size in bytes")
    
    # Processing information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    processing_log = models.TextField(blank=True)
    
    # Print settings
    print_quality = models.CharField(max_length=20, choices=PRINT_QUALITY_CHOICES, default='normal')
    infill_percentage = models.CharField(max_length=3, choices=INFILL_CHOICES, default='20')
    supports_needed = models.BooleanField(default=False)
    
    # Calculated information (from OrcaSlicer)
    estimated_print_time = models.CharField(max_length=50, blank=True)
    estimated_material_usage = models.FloatField(null=True, blank=True, help_text="Material usage in grams")
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Preview files
    preview_image = models.ImageField(upload_to='stl_previews/', blank=True, null=True)
    gcode_file = models.FileField(upload_to='gcode_files/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Admin flags
    approved_for_printing = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        user_info = self.user.username if self.user else f"Anonymous ({self.session_key})"
        return f"{self.name} - {user_info}"

    def get_absolute_url(self):
        return reverse('stl_uploads:detail', kwargs={'pk': self.pk})

    @property
    def file_size_mb(self):
        """Return file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def can_be_processed(self):
        """Check if file can be processed"""
        return self.status in ['uploaded', 'failed']

    def get_status_color(self):
        """Return Bootstrap color class for status"""
        status_colors = {
            'uploaded': 'secondary',
            'processing': 'warning',
            'processed': 'info',
            'failed': 'danger',
            'ready': 'success',
        }
        return status_colors.get(self.status, 'secondary')


class PrintOrder(models.Model):
    """Model for print orders based on STL files"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('printing', 'Printing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    stl_file = models.ForeignKey(STLFile, on_delete=models.CASCADE, related_name='print_orders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Order details
    quantity = models.PositiveIntegerField(default=1)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Customer information
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    delivery_address = models.TextField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    
    # Admin fields
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Print Order #{self.id} - {self.stl_file.name}"

    @property
    def total_estimated_time(self):
        """Calculate total estimated time for all quantities"""
        if self.stl_file.estimated_print_time and self.quantity:
            # This is a simplified calculation - you might want to make it more sophisticated
            return f"{self.quantity} × {self.stl_file.estimated_print_time}"
        return "Not calculated"