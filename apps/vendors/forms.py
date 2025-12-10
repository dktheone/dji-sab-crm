from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, HTML
from django_select2.forms import Select2Widget
from .models import (
    Vendor, VendorRegistrationID, VendorPayment, VendorDocument,
    BusinessType, VendorStatus, RegistrationIDType, PaymentMode, PaymentScheduleUnit, DocumentType
)


class VendorForm(forms.ModelForm):
    """Main vendor information form"""
    
    class Meta:
        model = Vendor
        fields = [
            'vendor_name', 'business_type', 'category', 'contact_person', 'designation',
            'mobile_no', 'mobile_no_2', 'email', 'address', 'city', 'state', 'pincode',
            'status', 'remarks'
        ]
        widgets = {
            'business_type': Select2Widget(attrs={'class': 'form-control custom_select'}),
            'state': Select2Widget(attrs={'class': 'form-control custom_select'}),
            'status': Select2Widget(attrs={'class': 'form-control custom_select'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'font-weight-bold'


class VendorRegistrationIDForm(forms.ModelForm):
    """Form for vendor registration IDs"""
    
    class Meta:
        model = VendorRegistrationID
        fields = ['id_type', 'id_number', 'is_primary', 'document_upload', 'verified', 'verification_date', 'remarks']
        widgets = {
            'id_type': Select2Widget(attrs={'class': 'form-control custom_select'}),
            'verification_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class VendorPaymentForm(forms.ModelForm):
    """Form for vendor payment information"""
    
    class Meta:
        model = VendorPayment
        fields = [
            'payment_mode', 'payment_schedule_value', 'payment_schedule_unit',
            'bank_name', 'account_holder_name', 'account_number', 'ifsc_code',
            'branch_name', 'upi_id', 'cancelled_cheque'
        ]
        widgets = {
            'payment_mode': Select2Widget(attrs={'class': 'form-control custom_select'}),
            'payment_schedule_unit': Select2Widget(attrs={'class': 'form-control custom_select'}),
            'payment_schedule_value': forms.NumberInput(attrs={'min': 1, 'placeholder': 'e.g., 7, 15, 30'}),
            'account_number': forms.TextInput(attrs={'placeholder': 'Enter bank account number'}),
            'ifsc_code': forms.TextInput(attrs={'placeholder': 'e.g., SBIN0001234', 'style': 'text-transform: uppercase;'}),
            'upi_id': forms.TextInput(attrs={'placeholder': 'e.g., vendor@upi'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        
        # Make bank fields not required initially (will be validated based on payment mode)
        bank_fields = ['bank_name', 'account_holder_name', 'account_number', 'ifsc_code', 'branch_name']
        for field_name in bank_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False

    def clean(self):
        cleaned_data = super().clean()
        payment_mode = cleaned_data.get('payment_mode')
        
        # Validate bank details for non-cash payment modes
        if payment_mode in [PaymentMode.CHEQUE, PaymentMode.NET_BANKING, PaymentMode.BANK_TRANSFER]:
            required_fields = {
                'bank_name': 'Bank Name',
                'account_number': 'Account Number',
                'ifsc_code': 'IFSC Code'
            }
            
            for field, label in required_fields.items():
                if not cleaned_data.get(field):
                    self.add_error(field, f'{label} is required for {payment_mode} payment mode.')
        
        return cleaned_data


class VendorDocumentForm(forms.ModelForm):
    """Form for vendor document uploads"""
    
    class Meta:
        model = VendorDocument
        fields = ['document_type', 'document_file', 'document_name', 'valid_until', 'remarks']
        widgets = {
            'document_type': Select2Widget(attrs={'class': 'form-control custom_select'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.fields['document_name'].required = False
        self.fields['valid_until'].required = False
        self.fields['remarks'].required = False

    def clean_document_file(self):
        document_file = self.cleaned_data.get('document_file')
        
        if document_file:
            # Check file size (max 5MB)
            if document_file.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must not exceed 5MB.')
            
            # Check file extension
            import os
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
            ext = os.path.splitext(document_file.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}')
        
        return document_file
