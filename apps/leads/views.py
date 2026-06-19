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
    from .models import CustomerType
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    employee_id = request.GET.get('employee', '').strip()
    customer_type = request.GET.get('customer_type', '').strip()

    # SECURITY: Get user role and current employee
    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    
    # Base queryset: Exclude invalid PKs for safety
    leads = Lead.objects.filter(pk__isnull=False).order_by('-entry_date')
    
    # SECURITY: 3-Tier Lead Visibility System
    # Tier 1: Admin / HR -> See all leads
    if user_role in ['admin', 'hr']:
        pass
    # Tier 2: Manager -> See own + same site employee leads
    elif user_role == 'manager':
        try:
            current_employee = Employee.objects.get(emp_code=request.user.username, status='Active')
            managed_site_employees = Employee.objects.filter(
                site=current_employee.site, status='Active'
            ).values_list('id', flat=True)
            leads = leads.filter(
                Q(created_by=current_employee) | 
                Q(created_by_id__in=managed_site_employees)
            )
        except Employee.DoesNotExist:
            messages.error(request, 'You must be linked to an active Employee record.')
            leads = Lead.objects.none()
    # Tier 3: Everyone else -> See own leads only
    else:
        try:
            current_employee = Employee.objects.get(emp_code=request.user.username, status='Active')
            leads = leads.filter(created_by=current_employee)
        except Employee.DoesNotExist:
            messages.error(request, 'You must be linked to an active Employee record to view leads.')
            leads = Lead.objects.none()

    # Pipeline stats computed based on role-filtered leads (before search/status queries are applied)
    total_count = leads.count()
    active_count = leads.filter(lead_status__in=['New', 'In Progress']).count()
    quoted_count = leads.filter(lead_status='Quoted').count()
    converted_count = leads.filter(lead_status='Converted').count()

    # Apply search and filters
    if query:
        leads = leads.filter(Q(client_name__icontains=query) | Q(contact_person__icontains=query))
    if status:
        leads = leads.filter(lead_status=status)
    if employee_id:
        leads = leads.filter(created_by_id=employee_id)
    if customer_type:
        leads = leads.filter(customer_type=customer_type)

    # Upcoming follow-ups count (only valid leads in current view)
    upcoming = leads.filter(next_follow_up__lte=timezone.now().date() + timezone.timedelta(days=7)).count()

    # Calculate if each lead has an overdue follow-up
    today = timezone.now().date()
    for l in leads:
        l.is_followup_overdue = False
        if l.next_follow_up and l.next_follow_up < today and l.lead_status not in ['Converted', 'Closed', 'Not Interested']:
            l.is_followup_overdue = True

    # Employees list for filter dropdown (Admin/HR can filter by employee)
    employees = Employee.objects.filter(status='Active').order_by('first_name')

    context = {
        'leads': leads,
        'employees': employees,
        'query': query,
        'status': status,
        'employee': employee_id,
        'customer_type': customer_type,
        'customer_types': CustomerType.choices,
        'upcoming_count': upcoming,
        'view_name': request.resolver_match.view_name,
        'can_view_all': user_role in ['admin', 'hr'],
        'total_count': total_count,
        'active_count': active_count,
        'quoted_count': quoted_count,
        'converted_count': converted_count,
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
            # Hard Block: Check for exact duplicate client name (case-insensitive) if creating a new lead
            client_name_val = form.cleaned_data.get('client_name', '').strip()
            if not lead and Lead.objects.filter(client_name__iexact=client_name_val).exists():
                existing_lead = Lead.objects.filter(client_name__iexact=client_name_val).first()
                form.add_error('client_name', f'A lead with this name already exists: "{existing_lead.client_name}" (ID: {existing_lead.lead_id}). Creation is blocked to prevent duplication.')
                messages.error(request, 'Creation blocked: A lead with this client name already exists.')
            else:
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

    # SECURITY FIX: Ensure the user owns the lead, is same-site manager, or is admin/hr
    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    if user_role not in ['admin', 'hr']:
        try:
            current_employee = Employee.objects.get(emp_code=request.user.username, status='Active')
            if user_role == 'manager':
                if lead.created_by != current_employee and lead.created_by.site != current_employee.site:
                    messages.error(request, 'You do not have permission to view or edit follow-ups for this lead.')
                    return redirect('leads:lead_list')
            else:
                if lead.created_by != current_employee:
                    messages.error(request, 'You do not have permission to view or edit follow-ups for this lead.')
                    return redirect('leads:lead_list')
        except Employee.DoesNotExist:
             messages.error(request, 'You must be linked to an active Employee record.')
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

    # SECURITY FIX: Ensure the user owns the lead, is same-site manager, or is admin/hr
    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    if user_role not in ['admin', 'hr']:
        try:
            current_employee = Employee.objects.get(emp_code=request.user.username, status='Active')
            if user_role == 'manager':
                if lead.created_by != current_employee and lead.created_by.site != current_employee.site:
                    messages.error(request, 'You do not have permission to convert this lead.')
                    return redirect('leads:lead_list')
            else:
                if lead.created_by != current_employee:
                    messages.error(request, 'You do not have permission to convert this lead.')
                    return redirect('leads:lead_list')
        except Employee.DoesNotExist:
            messages.error(request, 'You must be linked to an active Employee record.')
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
    
    # Access control:
    # 1. Admin/HR can view anyone's activity
    # 2. Manager can view their own, or anyone at the same site
    # 3. Employee can only view their own
    if user_role not in ['admin', 'hr']:
        if user_role == 'manager':
            if employee.site != current_employee.site and current_employee.id != employee.id:
                messages.error(request, 'You can only view activity of employees at your site.')
                logger.warning(f"Manager {request.user.username} attempted to view employee {employee_id}'s activity across sites")
                return redirect('leads:employee_activity', employee_id=current_employee.id)
        else:
            if current_employee.id != employee_id:
                messages.error(request, 'You can only view your own activity.')
                logger.warning(f"User {request.user.username} attempted to view employee {employee_id}'s activity without permission")
                return redirect('leads:employee_activity', employee_id=current_employee.id)
    
    # Fetch all leads for this employee with follow-ups prefetched (ordered by date descending)
    from django.db.models import Prefetch
    from datetime import date
    
    leads = Lead.objects.filter(
        created_by=employee, pk__isnull=False
    ).select_related('created_by', 'converted_site').prefetch_related(
        Prefetch('follow_ups', queryset=FollowUp.objects.order_by('-follow_up_date'))
    ).order_by('-entry_date')
    
    # Group leads by site
    from collections import OrderedDict
    site_groups = OrderedDict()
    
    for lead in leads:
        site_key = lead.converted_site.site_name if lead.converted_site else "Unassigned Leads"
        if site_key not in site_groups:
            site_groups[site_key] = []
            
        # Calculate time gaps between consecutive followups (prefetched ordered by -follow_up_date)
        follow_ups = list(lead.follow_ups.all())
        for i, fu in enumerate(follow_ups):
            if i + 1 < len(follow_ups):
                # Since list is descending, i is newer, i+1 is older
                gap = (fu.follow_up_date - follow_ups[i+1].follow_up_date).days
                fu.gap_days = gap
            else:
                fu.gap_days = None
            fu.days_ago = (date.today() - fu.follow_up_date).days
            
        # Flag stale leads (no followup/creation action in 14 days)
        lead.is_stale = False
        lead.days_since_activity = None
        if follow_ups:
            lead.days_since_activity = (date.today() - follow_ups[0].follow_up_date).days
            lead.is_stale = lead.days_since_activity > 14
        elif lead.entry_date:
            lead.days_since_activity = (date.today() - lead.entry_date).days
            lead.is_stale = lead.days_since_activity > 14
            
        lead.follow_up_list = follow_ups
        site_groups[site_key].append(lead)
        
    # Reorder site_groups so "Unassigned Leads" is at the bottom
    if "Unassigned Leads" in site_groups:
        unassigned = site_groups.pop("Unassigned Leads")
        site_groups["Unassigned Leads"] = unassigned
        
    # Summary stats
    total_leads = leads.count()
    active_leads = leads.filter(lead_status__in=['New', 'In Progress']).count()
    quoted_leads = leads.filter(lead_status='Quoted').count()
    converted_leads = leads.filter(lead_status='Converted').count()
    follow_ups_count = FollowUp.objects.filter(created_by=employee).count()
    
    conversion_rate = (
        (converted_leads / total_leads * 100) if total_leads > 0 else 0
    )
    
    # Switcher dropdown list for Admin/HR
    employees_list = None
    if user_role in ['admin', 'hr']:
        employees_list = Employee.objects.filter(status='Active').order_by('first_name', 'last_name')
        
    context = {
        'employee': employee,
        'site_groups': site_groups,
        'total_leads': total_leads,
        'active_leads': active_leads,
        'quoted_leads': quoted_leads,
        'conversions_count': converted_leads,
        'conversion_rate': round(conversion_rate, 1),
        'follow_ups_count': follow_ups_count,
        'view_name': request.resolver_match.view_name,
        'can_view_all': user_role in ['admin', 'hr'],
        'current_employee': current_employee,
        'employees_list': employees_list,
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


@role_required('sales', 'admin', 'hr', 'manager', 'employee')
def lead_search_api(request):
    """AJAX typeahead endpoint — search leads by client_name"""
    q = request.GET.get('q', '').strip()
    if len(q) < 3:
        return JsonResponse({'results': []})
    
    leads = Lead.objects.filter(
        client_name__icontains=q
    ).select_related('created_by').order_by('-entry_date')[:10]
    
    results = [{
        'lead_id': l.lead_id,
        'client_name': l.client_name,
        'customer_type': l.get_customer_type_display(),
        'address': (l.address or '')[:60],
        'lead_status': l.get_lead_status_display(),
        'status_raw': l.lead_status,
        'created_by': f"{l.created_by.first_name} {l.created_by.last_name}" if l.created_by else "Unknown",
        'edit_url': f"/leads/form/{l.lead_id}/"
    } for l in leads]
    
    return JsonResponse({'results': results, 'count': len(results)})


@role_required('sales', 'admin', 'hr', 'manager', 'employee')
def lead_contact_check_mobile(request):
    """Check if a mobile number already exists across all lead contacts"""
    mobile = request.GET.get('mobile', '').strip()
    contact_id = request.GET.get('contact_id', '').strip()
    if not mobile or len(mobile) < 8:
        return JsonResponse({'exists': False})
    
    query = Q(mobile1=mobile) | Q(mobile2=mobile)
    existing_qs = LeadContact.objects.filter(query).select_related('lead')
    if contact_id:
        existing_qs = existing_qs.exclude(id=contact_id)
        
    existing = existing_qs.first()
    if existing:
        return JsonResponse({
            'exists': True,
            'contact_name': existing.name,
            'lead_name': existing.lead.client_name,
            'lead_id': existing.lead.lead_id
        })
    return JsonResponse({'exists': False})