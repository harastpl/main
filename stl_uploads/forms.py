from django import forms
from .models import STLFile, PrintOrder


class STLUploadForm(forms.ModelForm):
    class Meta:
        model = STLFile
        fields = ['name', 'description', 'stl_file', 'print_quality', 'infill_percentage', 'supports_needed']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a name for your model'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your model (optional)'
            }),
            'stl_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.stl'
            }),
            'print_quality': forms.Select(attrs={'class': 'form-select'}),
            'infill_percentage': forms.Select(attrs={'class': 'form-select'}),
            'supports_needed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_stl_file(self):
        stl_file = self.cleaned_data.get('stl_file')
        if stl_file:
            # Check file extension
            if not stl_file.name.lower().endswith('.stl'):
                raise forms.ValidationError('Only STL files are allowed.')
            
            # Check file size (max 50MB)
            if stl_file.size > 50 * 1024 * 1024:
                raise forms.ValidationError('File size cannot exceed 50MB.')
        
        return stl_file


class PrintOrderForm(forms.ModelForm):
    class Meta:
        model = PrintOrder
        fields = ['quantity', 'customer_name', 'customer_email', 'customer_phone', 'delivery_address']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'value': 1
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91 9876543210'
            }),
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Complete delivery address'
            }),
        }


class STLProcessingForm(forms.ModelForm):
    """Form for admin to update processing settings"""
    class Meta:
        model = STLFile
        fields = ['print_quality', 'infill_percentage', 'supports_needed', 'approved_for_printing', 'admin_notes']
        widgets = {
            'print_quality': forms.Select(attrs={'class': 'form-select'}),
            'infill_percentage': forms.Select(attrs={'class': 'form-select'}),
            'supports_needed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'approved_for_printing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'admin_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Admin notes about this file...'
            }),
        }