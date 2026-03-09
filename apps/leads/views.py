# apps/leads/views.py (full updated file for completeness)
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.db import IntegrityError
from .models import Lead, FollowUp, LeadConversionLog, LeadStatus, LeadContact
from .forms import LeadForm, FollowUpForm, SiteConversionForm
from apps.emp.utils import role_required
from apps.emp.models import Employee, Site
from django.db.models import Count, Case, When, F, FloatField
from django.db.models.functions import Coalesce

logger = logging.getLogger(__name__)  # For production logging

@role_required('sales', 'admin', 'hr', 'manager', 'employee')
def lead_list(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    employee_id = request.GET.get('employee', '').strip()  # Use employee_id for clarity

    # SECURITY: Get user role and current employee
    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    
    # Base queryset: Exclude invalid PKs for safety
    leads = Lead.objects.filter(pk__isnull=False).order_by('-entry_date')
    
    # SECURITY: Non-admin/hr users can only see their own leads
    if user_role not in ['admin', 'hr']:
        try:
            current_employee = Employee.objects.get(emp_code=request.user.username, status='Active')
            leads = leads.filter(created_by=current_employee)
        except Employee.DoesNotExist:
            messages.error(request, 'You must be linked to an Employee record to view leads.')
            leads = Lead.objects.none()  # Return empty queryset

    if query:
        leads = leads.filter(Q(client_name__icontains=query) | Q(contact_person__icontains=query))
    if status:
        leads = leads.filter(lead_status=status)
    if employee_id:
        leads = leads.filter(created_by_id=employee_id)

    # Upcoming follow-ups count (only valid leads)
    upcoming = leads.filter(next_follow_up__lte=timezone.now().date() + timezone.timedelta(days=7)).count()

    # Employees: Only active ones, exclude None created_by
    employees = Employee.objects.filter(status='Active').order_by('first_name')

    context = {
        'leads': leads,
        'employees': employees,
        'query': query,
        'status': status,
        'employee': employee_id,  # For form repopulation
        'upcoming_count': upcoming,
        'view_name': request.resolver_match.view_name,
        'can_view_all': user_role in ['admin', 'hr'],  # Pass to template
    }
    return render(request, 'leads/lead_list.html', context)
@role_required('sales', 'admin', 'hr', 'manager', 'employee')
def lead_form(request, lead_id=None):
    lead = None
    if lead_id:
        try:
            # Fix: Use pk=lead_id (aliases to lead_id field) instead of id=lead_id
            lead = get_object_or_404(Lead, pk=lead_id)
            logger.info(f"Editing lead {lead.lead_id}: {lead.client_name}")
        except (Lead.DoesNotExist, ValueError) as e:
            logger.warning(f"Invalid lead_id {lead_id} in edit request: {e}")
            messages.error(request, f'Lead with ID {lead_id} not found. Please refresh the list.')
            return redirect('leads:lead_list')

    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            lead_instance = form.save(commit=False)
            if not lead:  # New lead
                # BUG FIX #4: Proper employee assignment with error handling
                try:
                    # Employee.user doesn't exist - link is username=emp_code
                    employee = Employee.objects.get(emp_code=request.user.username, status='Active')
                    lead_instance.created_by = employee
                except Employee.DoesNotExist:
                    messages.error(request, 'You must be linked to an Employee record to create leads. Contact admin.')
                    logger.error(f"User {request.user.username} attempted to create lead but has no Employee record")
                    return redirect('leads:lead_list')
            
            lead_instance.save()
            
            # Always redirect to edit mode to allow adding contacts
            if lead:  # Editing existing lead
                messages.success(request, f'Lead {lead_instance.client_name} updated successfully!')
            else:  # New lead - prompt to add contacts
                messages.success(request, f'Lead {lead_instance.client_name} saved successfully! Now add contacts below.')
            
            logger.info(f"Lead {lead_instance.lead_id} {'updated' if lead else 'created'} by {request.user.username}")
            return redirect('leads:lead_form', lead_id=lead_instance.lead_id)
        else:
            messages.error(request, 'Please correct the form errors below.')
            logger.warning(f"Form validation failed for lead {lead.lead_id if lead else 'new'}: {form.errors}")
    else:
        form = LeadForm(instance=lead)
        if lead:
            logger.info(f"Rendering edit form for lead {lead.lead_id}")

    context = {
        'form': form,
        'lead': lead,
        'title': f"Edit Lead {lead.lead_id}" if lead else "Add New Lead",
        'view_name': request.resolver_match.view_name,
    }
    return render(request, 'leads/lead_form.html', context)

@role_required('sales', 'admin', 'hr', 'manager', 'employee')
def lead_follow_ups(request, lead_id):
    lead = get_object_or_404(Lead, pk=lead_id)
    if not lead.pk:
        messages.error(request, 'Invalid lead.')
        return redirect('leads:lead_list')

    # SECURITY FIX: Ensure the user owns the lead or is admin/hr
    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    if user_role not in ['admin', 'hr']:
        try:
            current_employee = Employee.objects.get(emp_code=request.user.username, status='Active')
            if lead.created_by != current_employee:
                messages.error(request, 'You do not have permission to view or edit follow-ups for this lead.')
                return redirect('leads:lead_list')
        except Employee.DoesNotExist:
             messages.error(request, 'You must be linked to an Employee record.')
             return redirect('leads:lead_list')

    follow_ups = FollowUp.objects.filter(lead=lead).order_by('-follow_up_date')
    if request.method == 'POST':
        form = FollowUpForm(request.POST)
        if form.is_valid():
            follow_up = form.save(commit=False)
            follow_up.lead = lead
            # BUG FIX #4: Proper employee assignment
            try:
                employee = Employee.objects.get(emp_code=request.user.username, status='Active')
                follow_up.created_by = employee
            except Employee.DoesNotExist:
                messages.error(request, 'You must be linked to an Employee record.')
                return redirect('leads:lead_follow_ups', lead_id=lead_id)
            
            follow_up.save()
            messages.success(request, 'Follow-up added successfully!')
            return redirect('leads:lead_follow_ups', lead_id=lead_id)
    else:
        form = FollowUpForm(initial={'follow_up_date': timezone.now().date()})
    return render(request, 'leads/lead_follow_ups.html', {
        'lead': lead,
        'follow_ups': follow_ups,
        'form': form,
        'view_name': request.resolver_match.view_name
    })

@role_required('sales', 'admin', 'hr', 'manager', 'employee')
def convert_to_site(request, lead_id):
    lead = get_object_or_404(Lead, pk=lead_id)
    if not lead.pk or lead.lead_status == LeadStatus.CONVERTED:
        messages.error(request, 'Cannot convert this lead.')
        return redirect('leads:lead_list')

    # SECURITY FIX: Ensure the user owns the lead or is admin/hr
    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    if user_role not in ['admin', 'hr']:
        try:
            current_employee = Employee.objects.get(emp_code=request.user.username, status='Active')
            if lead.created_by != current_employee:
                messages.error(request, 'You do not have permission to convert this lead.')
                return redirect('leads:lead_list')
        except Employee.DoesNotExist:
            messages.error(request, 'You must be linked to an Employee record.')
            return redirect('leads:lead_list')

    if request.method == 'POST':
        form = SiteConversionForm(request.POST, lead=lead)
        if form.is_valid():
            try:
                site = form.save(commit=False)
                site.created_by = request.user
                site.save()

                lead.lead_status = LeadStatus.CONVERTED
                lead.converted_site = site
                lead.save()

                # BUG FIX #5: Proper employee for conversion log
                employee = None
                try:
                    employee = Employee.objects.get(emp_code=request.user.username, status='Active')
                except Employee.DoesNotExist:
                    # Let it be None, we should adjust the model if necessary or log it differently.
                    # As a fallback, we get the admin employee if one exists, but properly logged.
                    if user_role in ['admin', 'hr']:
                        employee = Employee.objects.filter(emp_code='admin').first() or Employee.objects.filter(status='Active').first()
                    logger.warning(f"User {request.user.username} has no Employee link, using fallback for conversion log")

                LeadConversionLog.objects.create(
                    lead=lead,
                    site=site,
                    converted_by=employee if employee else lead.created_by, # Fallback to lead creator if no employee found for current user
                    remarks=request.POST.get('conversion_remarks', f'Converted from Lead #{lead.lead_id}')
                )

                messages.success(request, f'Lead converted to Site: {site.site_name}.')
                logger.info(f"Lead {lead.lead_id} converted to Site {site.id} by {request.user.username}")
                return redirect('emp:site_crud')  # Or specific site view if exists
            except IntegrityError as e:
                logger.error(f"Conversion IntegrityError: {e}")
                form.add_error(None, 'Site name already exists. Please edit and retry.')
            except Exception as e:
                logger.error(f"Conversion error: {e}")
                messages.error(request, f'Conversion failed: {str(e)}')
        else:
            messages.error(request, 'Please correct form errors.')
    else:
        form = SiteConversionForm(lead=lead)
    return render(request, 'leads/convert_to_site.html', {'form': form, 'lead': lead, 'view_name': request.resolver_match.view_name})

# @role_required('admin', 'hr')
@role_required('sales', 'admin', 'hr', 'manager', 'employee')
def conversion_logs(request):
    logs = LeadConversionLog.objects.select_related('lead', 'site', 'converted_by').order_by('-conversion_date')
    return render(request, 'leads/conversion_logs.html', {'logs': logs, 'view_name': request.resolver_match.view_name})

# @role_required('sales', 'admin', 'hr')
# def employee_activity(request, employee_id):
#     employee = get_object_or_404(Employee, id=employee_id, status='Active')
#     leads = Lead.objects.filter(created_by=employee, pk__isnull=False)
#     follow_ups_count = FollowUp.objects.filter(created_by=employee).count()
#     conversions_count = LeadConversionLog.objects.filter(converted_by=employee).count()
#     return render(request, 'leads/employee_activity.html', {
#         'employee': employee,
#         'leads': leads,
#         'follow_ups_count': follow_ups_count,
#         'conversions_count': conversions_count,
#     })
    
    
# @role_required('sales', 'admin', 'hr', 'manager')
@role_required('sales', 'admin', 'hr', 'manager', 'employee')
def employee_activity(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id, status='Active')
    
    # SECURITY: Check if user has permission to view this employee's activity
    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    
    # Get current logged-in employee
    try:
        current_employee = Employee.objects.get(emp_code=request.user.username, status='Active')
    except Employee.DoesNotExist:
        messages.error(request, 'You must be linked to an Employee record.')
        return redirect('leads:lead_list')
    
    # Access control: Only admin/hr can view other employees' activity
    if user_role not in ['admin', 'hr']:
        if current_employee.id != employee_id:
            messages.error(request, 'You can only view your own activity.')
            logger.warning(f"User {request.user.username} attempted to view employee {employee_id}'s activity without permission")
            # Redirect to their own activity page
            return redirect('leads:employee_activity', employee_id=current_employee.id)
    
    # Leads created by this employee
    leads = Lead.objects.filter(created_by=employee, pk__isnull=False).select_related('created_by')
    
    # Follow-ups count and recent ones (last 10, ordered by date)
    follow_ups = FollowUp.objects.filter(created_by=employee).select_related('lead', 'created_by').order_by('-follow_up_date')[:10]
    follow_ups_count = FollowUp.objects.filter(created_by=employee).count()
    
    # Conversions (from logs)
    conversions = LeadConversionLog.objects.filter(converted_by=employee).select_related('lead', 'site').order_by('-conversion_date')
    conversions_count = conversions.count()
    
    # Computed: Conversion rate (leads converted / total leads * 100)
    total_leads = leads.count()
    converted_leads = Lead.objects.filter(created_by=employee, lead_status=LeadStatus.CONVERTED).count()
    conversion_rate = (
        (converted_leads / total_leads * 100) if total_leads > 0 else 0
    )
    
    context = {
        'employee': employee,
        'leads': leads,
        'follow_ups': follow_ups,
        'follow_ups_count': follow_ups_count,
        'conversions': conversions,
        'conversions_count': conversions_count,
        'conversion_rate': round(conversion_rate, 1),
        'total_leads': total_leads,
        'view_name': request.resolver_match.view_name,
        'can_view_all': user_role in ['admin', 'hr'],  # Pass to template
        'current_employee': current_employee,
    }
    return render(request, 'leads/employee_activity.html', context)

@role_required('sales', 'admin', 'hr', 'manager', 'employee')
def upcoming_followups(request):
    """View to show upcoming follow-ups for dashboard widget"""
    from datetime import date, timedelta
    
    # Get user role
    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    
    # Base queryset: leads with next_follow_up set and not converted/closed
    today = date.today()
    next_week = today + timedelta(days=300)
    
    followups = Lead.objects.filter(
        next_follow_up__isnull=False,
        next_follow_up__lte=next_week,
        lead_status__in=[LeadStatus.NEW, LeadStatus.IN_PROGRESS, LeadStatus.QUOTED]
    ).select_related('created_by').order_by('next_follow_up')
    
    # Role-based filtering
    if user_role not in ['admin', 'hr']:
        try:
            current_employee = Employee.objects.get(emp_code=request.user.username, status='Active')
            followups = followups.filter(created_by=current_employee)
        except Employee.DoesNotExist:
            followups = Lead.objects.none()
    
    # Mark overdue follow-ups
    for followup in followups:
        followup.is_overdue = followup.next_follow_up < today
        followup.is_today = followup.next_follow_up == today
    
    context = {
        'followups': followups,
        'today': today,
        'view_name': request.resolver_match.view_name
    }
    
    return render(request, 'leads/upcoming_followups.html', context)

@role_required('sales', 'admin', 'hr', 'manager', 'employee')
def my_activity(request):
    """Redirect to logged-in user's own activity page"""
    try:
        employee = Employee.objects.get(emp_code=request.user.username, status='Active')
        return redirect('leads:employee_activity', employee_id=employee.id)
    except Employee.DoesNotExist:
        messages.error(request, 'You must be linked to an Employee record to view activity.')
        return redirect('leads:lead_list')


# ==================== Lead Contact CRUD APIs ====================

@role_required('sales', 'admin', 'hr', 'manager', 'employee')
def lead_contacts_list(request, lead_id):
    """Get all contacts for a lead"""
    lead = get_object_or_404(Lead, lead_id=lead_id)
    contacts = lead.contacts.all()
    data = [{
        'id': c.id,
        'name': c.name,
        'designation': c.designation,
        'mobile1': c.mobile1,
        'mobile2': c.mobile2 or '',
        'landline': c.landline or '',
        'email': c.email or '',
        'remarks': c.remarks or '',
        'status': c.status
    } for c in contacts]
    return JsonResponse({'contacts': data})


@role_required('sales', 'admin', 'hr', 'manager', 'employee')
def all_lead_contacts(request):
    """Global view of all lead contacts with role-based filtering"""
    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    
    if user_role in ['admin', 'hr']:
        # Admin and HR see everything
        contacts = LeadContact.objects.select_related('lead').all().order_by('-created_at')
    else:
        # Sales folks only see contacts for leads they own
        try:
            employee = Employee.objects.get(emp_code=request.user.username, status='Active')
            contacts = LeadContact.objects.select_related('lead').filter(lead__created_by=employee).order_by('-created_at')
        except Employee.DoesNotExist:
            messages.error(request, 'You must be linked to an active Employee record.')
            return redirect('core:dashboard')
            
    return render(request, 'leads/all_contacts.html', {
        'contacts': contacts,
        'view_name': request.resolver_match.view_name
    })

@role_required('sales', 'admin', 'hr', 'manager', 'employee')
def lead_contact_create(request, lead_id):
    """Create new contact for lead"""
    import json
    if request.method == 'POST':
        try:
            lead = get_object_or_404(Lead, lead_id=lead_id)
            data = json.loads(request.body)
            
            contact = LeadContact.objects.create(
                lead=lead,
                name=data['name'],
                designation=data['designation'],
                mobile1=data['mobile1'],
                mobile2=data.get('mobile2', ''),
                landline=data.get('landline', ''),
                email=data.get('email', ''),
                remarks=data.get('remarks', ''),
                status=data.get('status', 'Active')
            )
            return JsonResponse({
                'success': True,
                'contact': {
                    'id': contact.id,
                    'name': contact.name,
                    'designation': contact.designation,
                    'mobile1': contact.mobile1,
                    'mobile2': contact.mobile2 or '',
                    'landline': contact.landline or '',
                    'email': contact.email or '',
                    'remarks': contact.remarks or '',
                    'status': contact.status
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@role_required('sales', 'admin', 'hr', 'manager', 'employee')
def lead_contact_update(request, contact_id):
    """Update contact"""
    import json
    if request.method == 'POST':
        try:
            contact = get_object_or_404(LeadContact, id=contact_id)
            data = json.loads(request.body)
            
            contact.name = data['name']
            contact.designation = data['designation']
            contact.mobile1 = data['mobile1']
            contact.mobile2 = data.get('mobile2', '')
            contact.landline = data.get('landline', '')
            contact.email = data.get('email', '')
            contact.remarks = data.get('remarks', '')
            contact.status = data.get('status', 'Active')
            contact.save()
            
            return JsonResponse({
                'success': True,
                'contact': {
                    'id': contact.id,
                    'name': contact.name,
                    'designation': contact.designation,
                    'mobile1': contact.mobile1,
                    'mobile2': contact.mobile2 or '',
                    'landline': contact.landline or '',
                    'email': contact.email or '',
                    'remarks': contact.remarks or '',
                    'status': contact.status
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@role_required('sales', 'admin', 'hr', 'manager', 'employee')
def lead_contact_delete(request, contact_id):
    """Delete contact"""
    if request.method == 'POST':
        try:
            contact = get_object_or_404(LeadContact, id=contact_id)
            contact.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)