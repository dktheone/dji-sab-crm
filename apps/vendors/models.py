from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from apps.emp.models import GENRAL_STATUS_CHOICES, STATE_CHOICES
from apps.emp.utils import generate_random_key
import os


def get_vendor_document_upload_path(instance, filename):
    """Generate upload path for vendor documents: media/uploads/vendors/{vendor_code}/documents/{random_key}_{filename}"""
    ext = os.path.splitext(filename)[1]
    random_key = generate_random_key()
    return os.path.join('uploads', 'vendors', instance.vendor.vendor_code, 'documents', f'{random_key}{ext}')


def get_vendor_id_upload_path(instance, filename):
    """Generate upload path for vendor registration ID documents"""
    ext = os.path.splitext(filename)[1]
    random_key = generate_random_key()
    return os.path.join('uploads', 'vendors', instance.vendor.vendor_code, 'registration_ids', f'{random_key}{ext}')


def get_cancelled_cheque_upload_path(instance, filename):
    """Generate upload path for cancelled cheque"""
    ext = os.path.splitext(filename)[1]
    random_key = generate_random_key()
    return os.path.join('uploads', 'vendors', instance.vendor.vendor_code, 'payment', f'cancelled_cheque_{random_key}{ext}')


class BusinessType(models.TextChoices):
    SUPPLIER = 'Supplier', 'Supplier'
    CONTRACTOR = 'Contractor', 'Contractor'
    SERVICE_PROVIDER = 'Service Provider', 'Service Provider'
    MANUFACTURER = 'Manufacturer', 'Manufacturer'
    DISTRIBUTOR = 'Distributor', 'Distributor'
    OTHER = 'Other', 'Other'


class VendorStatus(models.TextChoices):
    ACTIVE = 'Active', 'Active'
    INACTIVE = 'Inactive', 'Inactive'
    SUSPENDED = 'Suspended', 'Suspended'
    BLACKLISTED = 'Blacklisted', 'Blacklisted'


class RegistrationIDType(models.TextChoices):
    PAN_CARD = 'PAN Card', 'PAN Card'
    AADHAAR = 'Aadhaar', 'Aadhaar'
    GST = 'GST', 'GST'
    UDYAM = 'Udyam', 'Udyam'


class PaymentMode(models.TextChoices):
    CASH = 'Cash', 'Cash'
    CHEQUE = 'Cheque', 'Cheque'
    NET_BANKING = 'Net Banking', 'Net Banking'
    BANK_TRANSFER = 'Bank Transfer', 'Bank Transfer'
    UPI = 'UPI', 'UPI'


class PaymentScheduleUnit(models.TextChoices):
    DAYS = 'Days', 'Days'
    WEEKS = 'Weeks', 'Weeks'
    MONTHS = 'Months', 'Months'


class DocumentType(models.TextChoices):
    QUOTATION = 'Quotation', 'Quotation'
    CONTRACT = 'Contract', 'Contract'
    AGREEMENT = 'Agreement', 'Agreement'
    CANCELLED_CHEQUE = 'Cancelled Cheque', 'Cancelled Cheque'
    REGISTRATION_CERTIFICATE = 'Registration Certificate', 'Registration Certificate'
    OTHER = 'Other', 'Other'


class Vendor(models.Model):
    """Core vendor information model"""
    vendor_id = models.AutoField(primary_key=True)
    vendor_code = models.CharField(max_length=20, unique=True, editable=False)
    vendor_name = models.CharField(max_length=200, verbose_name="Vendor/Company Name")
    contact_person = models.CharField(max_length=100, verbose_name="Contact Person Name")
    designation = models.CharField(max_length=100, verbose_name="Designation")
    mobile_no = models.CharField(max_length=15, verbose_name="Mobile Number")
    mobile_no_2 = models.CharField(max_length=15, blank=True, null=True, verbose_name="Alternate Mobile")
    email = models.EmailField(blank=True, null=True, unique=True, verbose_name="Email Address")
    address = models.TextField(verbose_name="Complete Address")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="City")
    state = models.CharField(max_length=100, choices=STATE_CHOICES, blank=True, null=True, verbose_name="State")
    pincode = models.CharField(max_length=10, blank=True, null=True, verbose_name="PIN Code")
    business_type = models.CharField(max_length=30, choices=BusinessType.choices, verbose_name="Business Type")
    category = models.CharField(max_length=100, blank=True, null=True, verbose_name="Vendor Category")
    status = models.CharField(max_length=20, choices=VendorStatus.choices, default=VendorStatus.ACTIVE, verbose_name="Status")
    remarks = models.TextField(blank=True, null=True, verbose_name="Remarks/Notes")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendors_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendors'
        ordering = ['-created_at']
        verbose_name = "Vendor"
        verbose_name_plural = "Vendors"

    def __str__(self):
        return f"{self.vendor_code} - {self.vendor_name}"

    def save(self, *args, **kwargs):
        if not self.vendor_code:
            # Generate vendor_code (e.g., VEN0001)
            last_vendor = Vendor.objects.order_by('-vendor_id').first()
            if last_vendor:
                last_id = int(last_vendor.vendor_code.replace('VEN', ''))
                new_id = last_id + 1
            else:
                new_id = 1
            self.vendor_code = f'VEN{new_id:04d}'
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        # Validate unique vendor name (case-insensitive)
        if Vendor.objects.filter(vendor_name__iexact=self.vendor_name).exclude(vendor_id=self.vendor_id).exists():
            raise ValidationError({'vendor_name': 'A vendor with this name already exists.'})
        
        # Validate unique email if provided
        if self.email and Vendor.objects.filter(email=self.email).exclude(vendor_id=self.vendor_id).exists():
            raise ValidationError({'email': 'A vendor with this email already exists.'})

    @property
    def primary_registration_id(self):
        """Get the primary registration ID for this vendor"""
        return self.registration_ids.filter(is_primary=True).first()


class VendorRegistrationID(models.Model):
    """Multiple registration IDs for each vendor"""
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='registration_ids')
    id_type = models.CharField(max_length=20, choices=RegistrationIDType.choices, verbose_name="ID Type")
    id_number = models.CharField(max_length=50, verbose_name="ID Number")
    is_primary = models.BooleanField(default=False, verbose_name="Primary ID")
    document_upload = models.FileField(upload_to=get_vendor_id_upload_path, blank=True, null=True, verbose_name="ID Document")
    verified = models.BooleanField(default=False, verbose_name="Verified")
    verification_date = models.DateField(blank=True, null=True, verbose_name="Verification Date")
    remarks = models.TextField(blank=True, null=True, verbose_name="Remarks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendor_registration_ids'
        ordering = ['-is_primary', '-created_at']
        verbose_name = "Vendor Registration ID"
        verbose_name_plural = "Vendor Registration IDs"
        unique_together = ['vendor', 'id_type']  # One vendor can have only one PAN, one GST, etc.

    def __str__(self):
        primary = " (Primary)" if self.is_primary else ""
        return f"{self.vendor.vendor_code} - {self.id_type}: {self.id_number}{primary}"

    def clean(self):
        super().clean()
        # Validate ID format based on type
        if self.id_type == RegistrationIDType.PAN_CARD:
            if len(self.id_number) != 10:
                raise ValidationError({'id_number': 'PAN Card must be 10 characters long.'})
            if not self.id_number.isalnum():
                raise ValidationError({'id_number': 'PAN Card must be alphanumeric.'})
        
        elif self.id_type == RegistrationIDType.AADHAAR:
            if len(self.id_number) != 12:
                raise ValidationError({'id_number': 'Aadhaar must be 12 digits long.'})
            if not self.id_number.isdigit():
                raise ValidationError({'id_number': 'Aadhaar must contain only digits.'})
        
        elif self.id_type == RegistrationIDType.GST:
            if len(self.id_number) != 15:
                raise ValidationError({'id_number': 'GST number must be 15 characters long.'})
            if not self.id_number.isalnum():
                raise ValidationError({'id_number': 'GST number must be alphanumeric.'})
        
        elif self.id_type == RegistrationIDType.UDYAM:
            if len(self.id_number) != 19:
                raise ValidationError({'id_number': 'Udyam number must be 19 characters long.'})

    def save(self, *args, **kwargs):
        # If this is being set as primary, unset all other primary IDs for this vendor
        if self.is_primary:
            VendorRegistrationID.objects.filter(vendor=self.vendor, is_primary=True).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)


class VendorPayment(models.Model):
    """Payment and bank details for vendor"""
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name='payment_info')
    payment_mode = models.CharField(max_length=20, choices=PaymentMode.choices, verbose_name="Payment Mode")
    payment_schedule_value = models.PositiveIntegerField(verbose_name="Payment Schedule (Number)", validators=[MinValueValidator(1)])
    payment_schedule_unit = models.CharField(max_length=10, choices=PaymentScheduleUnit.choices, verbose_name="Payment Schedule Unit")
    
    # Bank Details
    bank_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bank Name")
    account_holder_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Account Holder Name")
    account_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Account Number")
    ifsc_code = models.CharField(
        max_length=11, 
        blank=True, 
        null=True, 
        verbose_name="IFSC Code",
        validators=[RegexValidator(regex=r'^[A-Z]{4}0[A-Z0-9]{6}$', message='Enter a valid IFSC code')]
    )
    branch_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Branch Name")
    upi_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="UPI ID")
    cancelled_cheque = models.FileField(upload_to=get_cancelled_cheque_upload_path, blank=True, null=True, verbose_name="Cancelled Cheque")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendor_payment_info'
        verbose_name = "Vendor Payment Information"
        verbose_name_plural = "Vendor Payment Information"

    def __str__(self):
        return f"{self.vendor.vendor_code} - {self.payment_mode}"

    @property
    def payment_schedule_display(self):
        """Return formatted payment schedule string"""
        value = self.payment_schedule_value
        unit = self.payment_schedule_unit
        return f"{value} {unit}"

    def clean(self):
        super().clean()
        # Validate bank details are provided for non-cash payment modes
        if self.payment_mode in [PaymentMode.CHEQUE, PaymentMode.NET_BANKING, PaymentMode.BANK_TRANSFER]:
            if not self.bank_name or not self.account_number or not self.ifsc_code:
                raise ValidationError({
                    'bank_name': 'Bank details are required for Cheque/Net Banking/Bank Transfer payment modes.',
                    'account_number': 'Bank account number is required.',
                    'ifsc_code': 'IFSC code is required.'
                })
        
        # Validate account number is numeric
        if self.account_number and not self.account_number.replace(' ', '').isdigit():
            raise ValidationError({'account_number': 'Account number must contain only digits.'})


class VendorDocument(models.Model):
    """Multiple documents for each vendor"""
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DocumentType.choices, verbose_name="Document Type")
    document_file = models.FileField(upload_to=get_vendor_document_upload_path, verbose_name="Document File")
    document_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Document Name/Description")
    upload_date = models.DateField(auto_now_add=True, verbose_name="Upload Date")
    valid_until = models.DateField(blank=True, null=True, verbose_name="Valid Until")
    remarks = models.TextField(blank=True, null=True, verbose_name="Remarks")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_documents_uploaded')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vendor_documents'
        ordering = ['-created_at']
        verbose_name = "Vendor Document"
        verbose_name_plural = "Vendor Documents"

    def __str__(self):
        return f"{self.vendor.vendor_code} - {self.document_type}"

    @property
    def file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.document_file.name)[1].lower()

    @property
    def file_size_mb(self):
        """Get file size in MB"""
        if self.document_file:
            return round(self.document_file.size / (1024 * 1024), 2)
        return 0

    def clean(self):
        super().clean()
        # Validate file size (max 5MB)
        if self.document_file and self.document_file.size > 5 * 1024 * 1024:
            raise ValidationError({'document_file': 'File size must not exceed 5MB.'})
        
        # Validate file extension
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
        if self.document_file:
            ext = os.path.splitext(self.document_file.name)[1].lower()
            if ext not in allowed_extensions:
                raise ValidationError({'document_file': f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'})
