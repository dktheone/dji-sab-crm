from django.contrib import admin
from .models import Vendor, VendorRegistrationID, VendorPayment, VendorDocument


class VendorRegistrationIDInline(admin.TabularInline):
    model = VendorRegistrationID
    extra = 1
    fields = ['id_type', 'id_number', 'is_primary', 'verified', 'verification_date']


class VendorDocumentInline(admin.TabularInline):
    model = VendorDocument
    extra = 0
    fields = ['document_type', 'document_file', 'document_name', 'valid_until']
    readonly_fields = ['upload_date', 'uploaded_by']


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['vendor_code', 'vendor_name', 'contact_person', 'mobile_no', 'business_type', 'status', 'created_at']
    list_filter = ['status', 'business_type', 'created_at']
    search_fields = ['vendor_code', 'vendor_name', 'contact_person', 'email', 'mobile_no']
    readonly_fields = ['vendor_code', 'created_at', 'updated_at', 'created_by']
    inlines = [VendorRegistrationIDInline, VendorDocumentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('vendor_code', 'vendor_name', 'business_type', 'category', 'status')
        }),
        ('Contact Details', {
            'fields': ('contact_person', 'designation', 'mobile_no', 'mobile_no_2', 'email')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'pincode')
        }),
        ('Additional Information', {
            'fields': ('remarks', 'created_by', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(VendorRegistrationID)
class VendorRegistrationIDAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'id_type', 'id_number', 'is_primary', 'verified', 'verification_date']
    list_filter = ['id_type', 'is_primary', 'verified']
    search_fields = ['vendor__vendor_name', 'vendor__vendor_code', 'id_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(VendorPayment)
class VendorPaymentAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'payment_mode', 'payment_schedule_display', 'bank_name', 'account_number']
    list_filter = ['payment_mode', 'payment_schedule_unit']
    search_fields = ['vendor__vendor_name', 'vendor__vendor_code', 'bank_name', 'account_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(VendorDocument)
class VendorDocumentAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'document_type', 'document_name', 'upload_date', 'valid_until', 'uploaded_by']
    list_filter = ['document_type', 'upload_date']
    search_fields = ['vendor__vendor_name', 'vendor__vendor_code', 'document_name']
    readonly_fields = ['upload_date', 'created_at', 'uploaded_by']
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
