from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
import json

from .models import Vendor, VendorRegistrationID, VendorPayment, VendorDocument
from .forms import VendorForm, VendorRegistrationIDForm, VendorPaymentForm, VendorDocumentForm


@login_required
def vendor_list(request):
    """Display list of all vendors"""
    vendors = Vendor.objects.all().select_related('payment_info').prefetch_related('registration_ids')
    
    # Apply filters if provided
    status_filter = request.GET.get('status')
    business_type_filter = request.GET.get('business_type')
    search_query = request.GET.get('search')
    
    if status_filter:
        vendors = vendors.filter(status=status_filter)
    
    if business_type_filter:
        vendors = vendors.filter(business_type=business_type_filter)
    
    if search_query:
        vendors = vendors.filter(
            Q(vendor_name__icontains=search_query) |
            Q(vendor_code__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    context = {
        'title': 'Vendor List',
        'vendors': vendors,
        'status_filter': status_filter,
        'business_type_filter': business_type_filter,
        'search_query': search_query,
    }
    return render(request, 'vendors/vendor_list.html', context)


@login_required
def vendor_create(request):
    """Create new vendor"""
    if request.method == 'POST':
        vendor_form = VendorForm(request.POST)
        
        if vendor_form.is_valid():
            try:
                with transaction.atomic():
                    # Create vendor
                    vendor = vendor_form.save(commit=False)
                    vendor.created_by = request.user
                    vendor.full_clean()  # Run model validation
                    vendor.save()
                    
                    messages.success(request, f'Vendor "{vendor.vendor_name}" created successfully! Now add registration IDs and payment information.')
                    return redirect('vendors:vendor_update', vendor_id=vendor.vendor_id)
            
            except ValidationError as e:
                # Handle validation errors
                for field, errors in e.message_dict.items():
                    for error in errors:
                        vendor_form.add_error(field, error)
            except Exception as e:
                messages.error(request, f'Error creating vendor: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        vendor_form = VendorForm()
    
    context = {
        'title': 'Add New Vendor',
        'form': vendor_form,
        'is_edit': False,
    }
    return render(request, 'vendors/vendor_form.html', context)


@login_required
def vendor_update(request, vendor_id):
    """Update existing vendor"""
    vendor = get_object_or_404(Vendor, vendor_id=vendor_id)
    
    if request.method == 'POST':
        vendor_form = VendorForm(request.POST, instance=vendor)
        
        if vendor_form.is_valid():
            try:
                vendor = vendor_form.save(commit=False)
                vendor.full_clean()
                vendor.save()
                messages.success(request, f'Vendor "{vendor.vendor_name}" updated successfully!')
                return redirect('vendors:vendor_detail', vendor_id=vendor.vendor_id)
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        vendor_form.add_error(field, error)
            except Exception as e:
                messages.error(request, f'Error updating vendor: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        vendor_form = VendorForm(instance=vendor)
    
    # Get existing registration IDs and payment info
    registration_ids = vendor.registration_ids.all()
    payment_info = getattr(vendor, 'payment_info', None)
    documents = vendor.documents.all()
    
    context = {
        'title': f'Edit Vendor - {vendor.vendor_code}',
        'form': vendor_form,
        'vendor': vendor,
        'registration_ids': registration_ids,
        'payment_info': payment_info,
        'documents': documents,
        'is_edit': True,
    }
    return render(request, 'vendors/vendor_form.html', context)


@login_required
def vendor_detail(request, vendor_id):
    """Display vendor details"""
    vendor = get_object_or_404(
        Vendor.objects.select_related('payment_info', 'created_by').prefetch_related('registration_ids', 'documents'),
        vendor_id=vendor_id
    )
    
    context = {
        'title': f'Vendor Details - {vendor.vendor_code}',
        'vendor': vendor,
    }
    return render(request, 'vendors/vendor_detail.html', context)


@login_required
def vendor_delete(request, vendor_id):
    """Delete vendor"""
    if request.method == 'POST':
        vendor = get_object_or_404(Vendor, vendor_id=vendor_id)
        vendor_name = vendor.vendor_name
        
        try:
            vendor.delete()
            messages.success(request, f'Vendor "{vendor_name}" deleted successfully!')
            return redirect('vendors:vendor_list')
        except Exception as e:
            messages.error(request, f'Error deleting vendor: {str(e)}')
            return redirect('vendors:vendor_detail', vendor_id=vendor_id)
    
    return redirect('vendors:vendor_list')


# ========== API Endpoints for AJAX Operations ==========

@login_required
def api_vendor_registration_ids(request, vendor_id):
    """Get all registration IDs for a vendor (AJAX)"""
    vendor = get_object_or_404(Vendor, vendor_id=vendor_id)
    registration_ids = vendor.registration_ids.all()
    
    data = {
        'registration_ids': [
            {
                'id': rid.id,
                'id_type': rid.id_type,
                'id_number': rid.id_number,
                'is_primary': rid.is_primary,
                'verified': rid.verified,
                'verification_date': rid.verification_date.strftime('%Y-%m-%d') if rid.verification_date else None,
                'document_url': rid.document_upload.url if rid.document_upload else None,
                'remarks': rid.remarks or '',
            }
            for rid in registration_ids
        ]
    }
    return JsonResponse(data)


@login_required
def api_vendor_registration_id_create(request, vendor_id):
    """Create new registration ID for vendor (AJAX)"""
    if request.method == 'POST':
        vendor = get_object_or_404(Vendor, vendor_id=vendor_id)
        
        try:
            data = json.loads(request.body)
            
            # Create registration ID
            reg_id = VendorRegistrationID(
                vendor=vendor,
                id_type=data.get('id_type'),
                id_number=data.get('id_number'),
                is_primary=data.get('is_primary', False),
                verified=data.get('verified', False),
                remarks=data.get('remarks', '')
            )
            reg_id.full_clean()
            reg_id.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Registration ID added successfully!',
                'registration_id': {
                    'id': reg_id.id,
                    'id_type': reg_id.id_type,
                    'id_number': reg_id.id_number,
                    'is_primary': reg_id.is_primary,
                }
            })
        
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def api_vendor_registration_id_update(request, reg_id):
    """Update registration ID (AJAX)"""
    if request.method == 'POST':
        registration_id = get_object_or_404(VendorRegistrationID, id=reg_id)
        
        try:
            data = json.loads(request.body)
            
            registration_id.id_type = data.get('id_type', registration_id.id_type)
            registration_id.id_number = data.get('id_number', registration_id.id_number)
            registration_id.is_primary = data.get('is_primary', registration_id.is_primary)
            registration_id.verified = data.get('verified', registration_id.verified)
            registration_id.remarks = data.get('remarks', registration_id.remarks)
            
            registration_id.full_clean()
            registration_id.save()
            
            return JsonResponse({'success': True, 'message': 'Registration ID updated successfully!'})
        
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def api_vendor_registration_id_delete(request, reg_id):
    """Delete registration ID (AJAX)"""
    if request.method == 'POST':
        registration_id = get_object_or_404(VendorRegistrationID, id=reg_id)
        
        try:
            registration_id.delete()
            return JsonResponse({'success': True, 'message': 'Registration ID deleted successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def vendor_payment_create_update(request, vendor_id):
    """Create or update vendor payment information"""
    vendor = get_object_or_404(Vendor, vendor_id=vendor_id)
    payment_info = getattr(vendor, 'payment_info', None)
    
    if request.method == 'POST':
        form = VendorPaymentForm(request.POST, request.FILES, instance=payment_info)
        
        if form.is_valid():
            try:
                payment = form.save(commit=False)
                payment.vendor = vendor
                payment.full_clean()
                payment.save()
                
                messages.success(request, 'Payment information saved successfully!')
                return redirect('vendors:vendor_update', vendor_id=vendor_id)
            
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
            except Exception as e:
                messages.error(request, f'Error saving payment information: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VendorPaymentForm(instance=payment_info)
    
    context = {
        'title': 'Vendor Payment Information',
        'vendor': vendor,
        'form': form,
    }
    return render(request, 'vendors/vendor_payment_form.html', context)


@login_required
def api_vendor_documents(request, vendor_id):
    """Get all documents for a vendor (AJAX)"""
    vendor = get_object_or_404(Vendor, vendor_id=vendor_id)
    documents = vendor.documents.all()
    
    data = {
        'documents': [
            {
                'id': doc.id,
                'document_type': doc.document_type,
                'document_name': doc.document_name or doc.document_type,
                'document_url': doc.document_file.url if doc.document_file else None,
                'upload_date': doc.upload_date.strftime('%Y-%m-%d'),
                'valid_until': doc.valid_until.strftime('%Y-%m-%d') if doc.valid_until else None,
                'file_size_mb': doc.file_size_mb,
                'remarks': doc.remarks or '',
            }
            for doc in documents
        ]
    }
    return JsonResponse(data)


@login_required
def api_vendor_document_upload(request, vendor_id):
    """Upload document for vendor (AJAX with file)"""
    if request.method == 'POST':
        vendor = get_object_or_404(Vendor, vendor_id=vendor_id)
        form = VendorDocumentForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                document = form.save(commit=False)
                document.vendor = vendor
                document.uploaded_by = request.user
                document.full_clean()
                document.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Document uploaded successfully!',
                    'document': {
                        'id': document.id,
                        'document_type': document.document_type,
                        'document_name': document.document_name or document.document_type,
                        'document_url': document.document_file.url,
                    }
                })
            
            except ValidationError as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        else:
            return JsonResponse({'success': False, 'error': form.errors.as_json()}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def api_vendor_document_delete(request, doc_id):
    """Delete vendor document (AJAX)"""
    if request.method == 'POST':
        document = get_object_or_404(VendorDocument, id=doc_id)
        
        try:
            # Delete file from storage
            if document.document_file:
                document.document_file.delete()
            
            document.delete()
            return JsonResponse({'success': True, 'message': 'Document deleted successfully!'})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
