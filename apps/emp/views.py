import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.views import PasswordResetView
from django.views.decorators.http import require_POST
from django.db.models import Sum, Q, F, Value, DecimalField, Max
from django.db.models import OuterRef, Subquery, Value, CharField
from django.db.models.functions import Coalesce
from django.db import models
from decimal import Decimal
from datetime import datetime
import calendar

from apps.emp.forms import DepartmentForm, DesignationForm, SitesForm, CustomLoginForm, CustomPasswordResetForm
from apps.emp.models import Department, Designation, Site
from apps.emp.models import Employee, EmployeeUpload, EmployeeStatus, EmployeeEducation, EmployeeExperience, EmployeeFamily, EmployeeSalaryMaster, EmployeeAdjustment, EmployeeSalaryTransaction
from apps.emp.forms import EmployeeForm, EmployeeUploadForm, EmployeeUserForm, EmployeeEducationForm, EmployeeExperienceForm, EmployeeFamilyForm, EmployeeSalaryMasterForm, EmployeeAdjustmentForm, SalaryPreparationForm
from apps.emp.utils import role_required, fetch_ifsc_details
from country_state_city import City

def custom_login(request):
    print('login request POST', request.POST, request.method)
    print('login request user', request.user)
    # if request.user.is_authenticated:
    #     return dashboard
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(username, password)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # return(dashboard)
                return JsonResponse({'status': 'success', 'redirect': '/dashboard/'})
            else:
                # form.add_error(None, "Invalid employee code or password")
                return JsonResponse({'status': 'error', 'message': 'Invalid employee code or password'}, status=400)
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})



def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('/login')  # Name of your login URL
    # return render(request, 'logout.html')

        
# def dashboard(request):
#     return render(request, "emp/dashboard.html")

def dashboard(request):
    # print('request', request.user)
    # print('$'* 20, 'request', request.user, request.user.is_authenticated)
    employee_id = request.user
    print(employee_id, request.user)
    print(request.user.is_authenticated, request.user.username)
    if request.user.is_authenticated:
        employee = get_object_or_404(Employee, emp_code=request.user.username) if employee_id else None
        print('$'* 20, 'employee', employee)
        return render(request, 'emp/dashboard.html', {
            'employee': employee
        })
    else:
        # print('#'* 20, 'request', request.user)
        return custom_logout(request)  # Name of your login URL    
        
    # # print('request.user.is_authenticated', request.user.is_authenticated)
    # if request.user.is_authenticated:
    #     return render(request, 'dashboard.html')
    # # return redirect('/login')
    


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_url = 'password-reset/done/'

@role_required('admin', 'hr')
def department_crud(request):
    if request.method == 'POST':
        if 'edit_id' in request.POST:
            # Handle edit form submission
            department = get_object_or_404(Department, id=request.POST['edit_id'])
            form = DepartmentForm(request.POST, instance=department)
            if form.is_valid():
                department = form.save(commit=False)
                department.created_by = request.user
                department.save()
                return JsonResponse({'status': 'success', 'message': 'Department updated successfully'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        else:
            # Handle add form submission
            form = DepartmentForm(request.POST)
            if form.is_valid():
                department = form.save(commit=False)
                department.created_by = request.user
                department.save()
                return JsonResponse({'status': 'success', 'message': 'Department added successfully'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    else:
        add_form = DepartmentForm()
        edit_form = DepartmentForm()  # Empty form for edit modal
        departments = Department.objects.all()
        return render(request, 'emp/department_crud.html', {
            'add_form': add_form,
            'edit_form': edit_form,
            'departments': departments
        })

@role_required('admin')
def delete_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    if request.method == 'POST':
        try:
            department.delete()
            return JsonResponse({'status': 'success', 'message': 'Department deleted successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@role_required('admin', 'hr')
def designation_crud(request):
    if request.method == 'POST':
        if 'edit_id' in request.POST:
            # Handle edit form submission
            designation = get_object_or_404(Designation, id=request.POST['edit_id'])
            print('designation', designation)
            print('request.POST', request.POST)
            form = DesignationForm(request.POST, instance=designation)
            print('form', form, form.is_valid())
            if form.is_valid():
                designation = form.save(commit=False)
                designation.created_by = request.user
                designation.save()
                messages.success(request, message="Designation updated successfully")
                # return render(request, 'emp/designation_crud.html')
                return JsonResponse({'status': 'success', 'message': 'Designation updated successfully'})
            else:
                messages.error(message="Designation Updation Failed!")
                # return render(request, 'emp/designation_crud.html')
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        else:
            # Handle add form submission
            form = DesignationForm(request.POST)
            if form.is_valid():
                designation = form.save(commit=False)
                designation.created_by = request.user
                designation.save()
                messages.success(request, message="Designation Added successfully")
                # return render(request, 'emp/designation_crud.html')
                return JsonResponse({'status': 'success', 'message': 'Designation added successfully'})
            else:
                messages.error(request, message="Designation Insertion Failed!")
                # return render(request, 'emp/designation_crud.html')
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    else:
        add_form = DesignationForm()
        edit_form = DesignationForm()  # Empty form for edit modal
        designations = Designation.objects.all()
        return render(request, 'emp/designation_crud.html', {
            'add_form': add_form,
            'edit_form': edit_form,
            'designations': designations
        })

@role_required('admin')
def delete_designation(request, designation_id):
    designation = get_object_or_404(Designation, id=designation_id)
    if request.method == 'POST':
        try:
            designation.delete()
            return JsonResponse({'status': 'success', 'message': 'Designation deleted successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@role_required('admin', 'hr', 'employee')
def site_crud(request, site_id=None):
    site_details = get_object_or_404(Site, id=site_id) if site_id else None
    if request.method == 'POST':
        if 'edit_id' in request.POST:
            # Handle edit form submission
            site = get_object_or_404(Site, id=request.POST['edit_id'])
            form = SitesForm(request.POST, instance=site)
            if form.is_valid():
                site = form.save(commit=False)
                site.created_by = request.user
                site.save()
                messages.success(request, "Site updated successfully")
                return JsonResponse({'status': 'success', 'message': 'Site updated successfully'})
            else:
                messages.error(request, "Site Updation Failed!")
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        else:
            # Handle add form submission
            form = SitesForm(request.POST)
            if form.is_valid():
                site = form.save(commit=False)
                site.created_by = request.user
                site.save()
                messages.success(request, "New Site Added successfully")
                return JsonResponse({'status': 'success', 'message': 'New Site added successfully'})
            else:
                messages.error(request, "New Site Insertion Failed!")
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    else:
        add_form = SitesForm()
        edit_form = SitesForm(instance=site_details) if site_details else SitesForm()
        sites = Site.objects.all()
        initial_city = site_details.city if site_details else None
        initial_state = site_details.state if site_details else None
        return render(request, 'emp/sites_crud.html', {
            'site_add_form': add_form,
            'site_edit_form': edit_form,
            'sites': sites,
            'initial_city': initial_city,
            'initial_state': initial_state,
            'site_details': site_details,
        })

@role_required('admin')
def delete_site(request, site_id):
    site = get_object_or_404(Site, id=site_id)
    if request.method == 'POST':
        try:
            site.delete()
            return JsonResponse({'status': 'success', 'message': 'Site deleted successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@role_required('admin', 'hr', 'employee')
def employee_form(request, employee_id=None):
    employee = get_object_or_404(Employee, id=employee_id) if employee_id else None
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.created_by = request.user
            employee.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Employee saved successfully',
                'redirect': f'/emp/upload/{employee.id}/'
            })
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors, 'test': '7275'}, status=400)
    else:
        employee_form = EmployeeForm(instance=employee)
        initial_city = employee.cor_city if employee else None
        initial_state = employee.cor_state if employee else None
        return render(request, 'emp/employee_form.html', {
            'employee_form': employee_form,
            'employee': employee,
            'initial_city': initial_city,
            'initial_state': initial_state,
            'step': 1  # For wizard indicator
        })
# New view for additional details (Education, Experience, Family)
@role_required('admin', 'hr', 'employee')
def employee_additional(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    # if request.user.groups.filter(name='employee').exists() and employee.created_by != request.user:
    #     return redirect('emp:employee_list')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_education' or action == 'edit_education':
            instance = get_object_or_404(EmployeeEducation, id=request.POST.get('id')) if action == 'edit_education' else None
            form = EmployeeEducationForm(request.POST, instance=instance)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.employee = employee
                obj.created_by = request.user
                obj.save()
                return JsonResponse({'status': 'success', 'message': 'Education saved successfully'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        elif action == 'delete_education':
            instance = get_object_or_404(EmployeeEducation, id=request.POST.get('id'))
            instance.delete()
            return JsonResponse({'status': 'success', 'message': 'Education deleted successfully'})
        # Similar for experience
        elif action == 'add_experience' or action == 'edit_experience':
            instance = get_object_or_404(EmployeeExperience, id=request.POST.get('id')) if action == 'edit_experience' else None
            form = EmployeeExperienceForm(request.POST, instance=instance)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.employee = employee
                obj.created_by = request.user
                obj.save()
                return JsonResponse({'status': 'success', 'message': 'Experience saved successfully'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        elif action == 'delete_experience':
            instance = get_object_or_404(EmployeeExperience, id=request.POST.get('id'))
            instance.delete()
            return JsonResponse({'status': 'success', 'message': 'Experience deleted successfully'})
        # Similar for family
        elif action == 'add_family' or action == 'edit_family':
            instance = get_object_or_404(EmployeeFamily, id=request.POST.get('id')) if action == 'edit_family' else None
            form = EmployeeFamilyForm(request.POST, instance=instance)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.employee = employee
                obj.created_by = request.user
                obj.save()
                return JsonResponse({'status': 'success', 'message': 'Family member saved successfully'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        elif action == 'delete_family':
            instance = get_object_or_404(EmployeeFamily, id=request.POST.get('id'))
            instance.delete()
            return JsonResponse({'status': 'success', 'message': 'Family member deleted successfully'})

    education_form = EmployeeEducationForm()
    experience_form = EmployeeExperienceForm()
    family_form = EmployeeFamilyForm()
    educations = EmployeeEducation.objects.filter(employee=employee)
    experiences = EmployeeExperience.objects.filter(employee=employee)
    families = EmployeeFamily.objects.filter(employee=employee)

    return render(request, 'emp/employee_additional.html', {
        'employee': employee,
        'education_form': education_form,
        'experience_form': experience_form,
        'family_form': family_form,
        'educations': educations,
        'experiences': experiences,
        'families': families,
        'step': 2  # For wizard indicator
    })
    
    
@role_required('admin', 'hr', 'employee')
def employee_uploads(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    # if request.user.groups.filter(name='employee').exists() and employee.created_by != request.user:
    #     return redirect('emp:employee_list')
    
    if request.method == 'POST':
        upload_form = EmployeeUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            upload = upload_form.save(commit=False)
            upload.employee = employee
            upload.uploaded_by = request.user
            upload.created_by = request.user
            upload.save()
            return JsonResponse({'status': 'success', 'message': 'Document uploaded successfully'})
        else:
            return JsonResponse({'status': 'error', 'errors': upload_form.errors}, status=400)
    else:
        upload_form = EmployeeUploadForm()
        uploads = EmployeeUpload.objects.filter(employee=employee)
        return render(request, 'emp/employee_uploads.html', {
            'upload_form': upload_form,
            'employee': employee,
            'uploads': uploads,
            'step': 3  # For wizard indicator
        })


@require_POST
def get_ifsc_data(request):
    ifsc_code = request.POST.get('ifsc_code', '').strip().upper() # Get from POST data, clean, and make uppercase

    ifsc_details = fetch_ifsc_details(ifsc_code)

    if "error" in ifsc_details:
        return JsonResponse({"status": "error", "message": ifsc_details["error"]}, status=400)
    else:
        return JsonResponse({"status": "success", "data": ifsc_details})


@role_required('admin', 'hr')
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'emp/employee_list.html', {
        'employees': employees,
        'status_choices': EmployeeStatus.choices
    })
    
    
# @role_required('admin', 'hr')
# def employee_view(request, employee_id):
#     employee = get_object_or_404(Employee, id=employee_id)
#     uploads = EmployeeUpload.objects.filter(employee=employee)
#     return render(request, 'emp/employee_view.html', {'employee': employee, 'uploads': uploads})

@role_required('admin', 'hr', 'employee')
def employee_view(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    # if request.user.groups.filter(name='employee').exists() and employee.created_by != request.user:
    #     return redirect('emp:employee_list')
    
    educations = EmployeeEducation.objects.filter(employee=employee)
    experiences = EmployeeExperience.objects.filter(employee=employee)
    families = EmployeeFamily.objects.filter(employee=employee)
    uploads = EmployeeUpload.objects.filter(employee=employee)
    
    return render(request, 'emp/employee_view.html', {
        'employee': employee,
        'educations': educations,
        'experiences': experiences,
        'families': families,
        'uploads': uploads,
        'step': 4  # For wizard indicator
    })


@role_required('admin', 'hr')
def update_employee_status(request, employee_id):
    print(request, employee_id, request.POST.get('status'))
    if request.method == 'POST':
        employee = get_object_or_404(Employee, id=employee_id)
        
        print(employee)
        
        status = request.POST.get('status')
        status_split =  list(status)
        print(status_split)
        print((status in [choice[0] for choice in EmployeeStatus.choices]), status)
        print([choice[0] for choice in EmployeeStatus.choices])
        
        # print(type(status), [type(choice[0]) for choice in EmployeeStatus.choices], (status in [choice[0] for choice in EmployeeStatus.choices]))
        # for choice in EmployeeStatus.choices:
        #     print(choice[0], status, (status == choice[0]) )
        #     print(len(choice[0]), len(status), (len(status) == len(choice[0])))
        
        if status in [choice[0] for choice in EmployeeStatus.choices]:
            print('status', status)
            employee.status = status
            employee.save()
            return JsonResponse({'status': 'success', 'message': 'Status updated successfully'})
        return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)





def get_cities(request):
    if request.method == 'GET':
        state_code = request.GET.get('state_code')
        if state_code:
            cities = City.get_cities_of_state('IN', state_code)
            city_choices = [(city.name, city.name) for city in cities]
            return JsonResponse({'cities': city_choices})
        return JsonResponse({'cities': []}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)



@role_required('admin', 'hr')
def create_employee_user(request):
    
    # User = get_user_model()
    if request.method == 'POST':
        form = EmployeeUserForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            try:
                user = User.objects.create_user(
                    username=employee.emp_code,
                    password=employee.emp_code,
                    email=employee.email or '',
                    first_name=employee.first_name,
                    last_name=employee.last_name
                    # emp_id=employee.id
                )
                employee_group = Group.objects.get(name='employee')
                user.groups.add(employee_group)
                user.save()
                return JsonResponse({'status': 'success', 'message': f'User created for {employee.emp_code}'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    else:
        form = EmployeeUserForm()
        return render(request, 'emp/create_employee_user.html', {'form': form})
    
    

from django.views.generic import ListView
from django.db.models import Q, Case, When, Value, CharField, Count
from django.utils import timezone
    
# @role_required('admin', 'hr')
class EmployeeDashboardView(ListView):
    model = Employee
    template_name = 'emp/employee_dashboard.html'
    context_object_name = 'employees'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset().filter(status__in=['Active', 'Onboarding', 'Probation'])
        current_month = timezone.now().month
        current_year = timezone.now().year

        # Annotate statuses
        queryset = queryset.annotate(
            payroll_status=Case(
                When(salary_transactions__month=current_month, salary_transactions__year=current_year,
                     salary_transactions__status__in=['Prepared', 'Paid'], then=Value('Processed')),
                default=Value('Pending'),
                output_field=CharField()
            ),
            login_status=Case(
                When(emp_code__in=User.objects.filter(is_active=True).values('username'), then=Value('Active')),
                When(emp_code__in=User.objects.filter(is_active=False).values('username'), then=Value('Disabled')),
                default=Value('Not Created'),
                output_field=CharField()
            ),
            salary_status=Case(
                When(salary_masters__status='Active', salary_masters__effective_from__lte=timezone.now(),
                     then=Value('Assigned')),
                default=Value('Pending'),
                output_field=CharField()
            ),
            adjustments_status=Case(
                When(adjustments__status='PENDING', then=Value('Pending')),
                default=Value('No Pending'),
                output_field=CharField()
            )
        ).distinct()

        # Apply quick filters
        filter_type = self.request.GET.get('filter')
        if filter_type == 'payroll_pending':
            queryset = queryset.filter(payroll_status='Pending')
        elif filter_type == 'login_not_created':
            queryset = queryset.filter(login_status='Not Created')
        elif filter_type == 'salary_pending':
            queryset = queryset.filter(salary_status='Pending')
        elif filter_type == 'adjustments_pending':
            queryset = queryset.filter(adjustments_status='Pending')

        # Apply advanced filters
        dept = self.request.GET.get('dept')
        if dept:
            queryset = queryset.filter(department__department_name=dept)
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(emp_code__icontains=search) |
                Q(department__department_name__icontains=search)
            )

        return queryset.order_by('first_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_month = timezone.now().month
        current_year = timezone.now().year
        qs = Employee.objects.filter(status__in=['Active', 'Onboarding', 'Probation'])

        # Stat cards data
        context['stats'] = {
            'total_employees': qs.count(),
            'payroll_pending': qs.filter(
                ~Q(salary_transactions__month=current_month, salary_transactions__year=current_year)
            ).count(),
            'login_not_created': qs.filter(
                ~Q(emp_code__in=User.objects.values('username'))
            ).count(),
            'salary_processed': qs.filter(
                salary_masters__status='Active',
                salary_masters__effective_from__lte=timezone.now()
            ).count(),
            'adjustments_pending': qs.filter(adjustments__status='PENDING').count(),
        }
        context['departments'] = Department.objects.filter(status='Active').values_list('department_name', flat=True)
        context['statuses'] = [choice[0] for choice in EmployeeStatus.choices]
        context['current_filter'] = self.request.GET.get('filter', 'all')
        return context   
    
    

# region SALARY_OLD
# @role_required('admin', 'hr')
# def salary_master_list(request):
#     employees = Employee.objects.filter(status='Active')
#     return render(request, 'emp/salary_master_list.html', {'employees': employees})

@role_required('admin', 'hr')
def salary_master_form(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        form = EmployeeSalaryMasterForm(request.POST)
        if form.is_valid():
            salary_master = form.save(commit=False)
            salary_master.employee = employee
            salary_master.created_by = request.user
            salary_master.save()
            return JsonResponse({'status': 'success', 'message': 'Salary master saved'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    form = EmployeeSalaryMasterForm()
    masters = EmployeeSalaryMaster.objects.filter(employee=employee)
    return render(request, 'emp/salary_master_form.html', {'form': form, 'employee': employee, 'masters': masters})

@role_required('admin', 'hr')
def adjustments_list(request):
    employees = Employee.objects.filter(status='Active')
    return render(request, 'emp/adjustments_list.html', {'employees': employees})

@role_required('admin', 'hr')
def adjustments_form(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        form = EmployeeAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = form.save(commit=False)
            adjustment.employee = employee
            adjustment.created_by = request.user
            adjustment.save()
            return JsonResponse({'status': 'success', 'message': 'Adjustment saved'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    form = EmployeeAdjustmentForm()
    adjustments = EmployeeAdjustment.objects.filter(employee=employee)
    return render(request, 'emp/adjustments_form.html', {'form': form, 'employee': employee, 'adjustments': adjustments})

# @role_required('admin', 'hr')
# def salary_preparation(request):
#     month = request.GET.get('month', datetime.now().month)
#     year = request.GET.get('year', datetime.now().year)
#     site = request.GET.get('site', 'ALL')
#     months = [datetime(1900, i, 1).strftime('%B') for i in range(1, 13)]

#     employees = Employee.objects.filter(status='Active')
#     if site != 'ALL':
#         employees = employees.filter(site=site)

#     # Proper correlated subquery
#     salary_txn = EmployeeSalaryTransaction.objects.filter(
#         employee_id=OuterRef('id'),
#         month=month,
#         year=year
#     ).values('status')[:1]

#     employees = employees.annotate(
#         prepared=Coalesce(
#             Subquery(salary_txn, output_field=CharField()),
#             Value('Not Prepared'),
#             output_field=CharField()
#         )
#     )
#     # print(employees)
#     # for emp in employees:
#     #     print(emp, emp.id, emp.status)
#     sites = Site.objects.all()  # Assuming Site model exists
#     return render(request, 'emp/salary_preparation.html', {
#         'employees': employees,
#         'month': month,
#         'months': months,
#         'year': year,
#         'site': site,
#         'sites': sites,
#     })

@role_required('admin', 'hr')
def make_salary(request, employee_id):
    # print("request.POST.get('month')")
    # print("employee_id", employee_id)
    # print(request)
    employee = get_object_or_404(Employee, id=employee_id)
    month = int(request.POST.get('month', datetime.now().month))
    # month = 8 # For testing, hardcoded to August
    print('month', month)
    year = int(request.POST.get('year', datetime.now().year))

    # Check if already prepared
    if EmployeeSalaryTransaction.objects.filter(employee=employee, month=month, year=year).exists():
        return JsonResponse({'status': 'error', 'message': 'Salary already prepared for this month'})

    # Get active salary 2025-05-01
    active_salary = EmployeeSalaryMaster.objects.filter(
        employee=employee, status='Active', effective_from__lte=datetime(year, month, 1)
    ).order_by('-effective_from').first()

    if not active_salary:
        return JsonResponse({'status': 'error', 'message': 'No active salary master found'})

    salary_amount = active_salary.salary_amount

    # Get adjustments for the month
    adjustments = EmployeeAdjustment.objects.filter(
        employee=employee,
        date__month=month,
        date__year=year,
    ).annotate(
        signed_amount=Coalesce(
            models.Case(
                models.When(adjustment_type='Allowance', then=F('amount')),
                models.When(adjustment_type__in=['Deduction', 'Advance'], then=-F('amount')),
                output_field=DecimalField(),
            ), Value(Decimal('0'))
        )
    ).aggregate(net_adjust=Sum('signed_amount'))['net_adjust'] or Decimal('0')

    form = SalaryPreparationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        leave_days = form.cleaned_data['leave_days']
        remarks = form.cleaned_data['remarks']

        # Assume 30 days month
        per_day = salary_amount / Decimal('30')
        leave_deduction = per_day * Decimal(leave_days)

        net_salary = salary_amount + adjustments - leave_deduction

        transaction = EmployeeSalaryTransaction(
            employee=employee,
            month=month,
            year=year,
            salary_amount=salary_amount,
            adjustments_net=adjustments,
            leave_days=leave_days,
            leave_deduction=leave_deduction,
            net_salary=net_salary,
            prepared_by=request.user,
            remarks=remarks
        )
        transaction.save()
        return JsonResponse({'status': 'success', 'message': 'Salary prepared successfully'})

    # For GET, prepare data for modal
    previous_transactions = EmployeeSalaryTransaction.objects.filter(employee=employee).order_by('-year', '-month')[:3]
    current_adjustments = EmployeeAdjustment.objects.filter(employee=employee, date__month=month, date__year=year)
    
    data = {
        'salary_amount': float(salary_amount),
        'adjustments': list(current_adjustments.values()),
        'previous_transactions': list(previous_transactions.values()),
        'form': form.as_p(),  # Or use crispy
    }
    return JsonResponse(data)

# endregion SALARY_OLD

    
    
# region SALARY
@role_required('admin', 'hr')
def salary_master_list(request):
    # Employees without any salary
    no_salary_employees = Employee.objects.filter(salary_masters__isnull=True, status='Active')
    # Employees with latest active salary
    with_salary_employees = Employee.objects.filter(status='Active').annotate(
        latest_salary=Max('salary_masters__effective_from')
    ).filter(salary_masters__effective_from=F('latest_salary'), salary_masters__status='Active').prefetch_related('salary_masters')
    return render(request, 'emp/salary_master_list.html', {
        'no_salary_employees': no_salary_employees,
        'with_salary_employees': with_salary_employees
    })

@role_required('admin', 'hr')
def salary_master_detail(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)
    salaries = EmployeeSalaryMaster.objects.filter(employee=employee).order_by('-effective_from')
    latest_salary = salaries.first()
    if request.method == 'POST':
        if latest_salary and 'edit' in request.POST:
            form = EmployeeSalaryMasterForm(request.POST, instance=latest_salary)
        else:
            form = EmployeeSalaryMasterForm(request.POST)
        if form.is_valid():
            salary = form.save(commit=False)
            salary.employee = employee
            salary.created_by = request.user
            salary.save()
            return redirect('apps.emp:salary_master_detail', emp_id=emp_id)
    else:
        form = EmployeeSalaryMasterForm(instance=latest_salary) if latest_salary else EmployeeSalaryMasterForm()
    return render(request, 'emp/salary_master_detail.html', {
        'employee': employee,
        'salaries': salaries,
        'form': form,
        'latest_salary': latest_salary
    })

@role_required('admin', 'hr')
def adjustments_page(request):
    if request.method == 'POST':
        form = EmployeeAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = form.save(commit=False)
            adjustment.created_by = request.user
            adjustment.save()
            return redirect('apps.emp:adjustments_page')
    else:
        form = EmployeeAdjustmentForm()
    adjustments = EmployeeAdjustment.objects.all()
    return render(request, 'emp/adjustments.html', {'form': form, 'adjustments': adjustments})

@role_required('admin', 'hr')
def salary_preparation(request):
    current_month = datetime.now().month
    current_year = datetime.now().year
    site = request.GET.get('site')
    department = request.GET.get('department')
    designation = request.GET.get('designation')
    queryset = Employee.objects.filter(status='Active')
    if site:
        queryset = queryset.filter(site__id=site)
    if department:
        queryset = queryset.filter(department__id=department)
    if designation:
        queryset = queryset.filter(designation__id=designation)
    # Pending adjustments summary
    queryset = queryset.annotate(
        pending_adjustments=Coalesce(Sum('adjustments__amount', filter=Q(adjustments__status__in=['Pending', 'Partial'], adjustments__date__month=current_month, adjustments__date__year=current_year)), Decimal('0'))
    )
    sites = Site.objects.all()
    departments = Department.objects.all()
    designations = Designation.objects.all()
    return render(request, 'emp/salary_preparation.html', {
        'employees': queryset,
        'sites': sites,
        'departments': departments,
        'designations': designations,
        'current_month': current_month,
        'current_year': current_year,
    })

@role_required('admin', 'hr')
def prepare_salary(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)
    current_month = datetime.now().month
    current_year = datetime.now().year
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    latest_salary = EmployeeSalaryMaster.objects.filter(employee=employee, status='Active').order_by('-effective_from').first()
    if not latest_salary:
        return JsonResponse({'status': 'error', 'message': 'No active salary'}, status=400)
    pending_adjustments = EmployeeAdjustment.objects.filter(employee=employee, status__in=['Pending', 'Partial'], date__month=current_month, date__year=current_year)
    last_3_adjustments = EmployeeAdjustment.objects.filter(employee=employee).order_by('-date')[:3]
    last_3_salaries = EmployeeSalaryTransaction.objects.filter(employee=employee).order_by('-year', '-month')[:3]
    if request.method == 'POST':
        days_absent = int(request.POST.get('days_absent', 2))
        leave_deduction = (latest_salary.salary_amount / days_in_month) * days_absent
        adjustments_net = Decimal('0')
        for adj in pending_adjustments:
            partial = Decimal(request.POST.get(f'partial_{adj.id}', '0'))
            if partial > adj.remaining_amount:
                return JsonResponse({'status': 'error', 'message': 'Partial exceeds remaining'}, status=400)
            if partial > 0:
                adj.remaining_amount -= partial
                adj.save()
            # Net: + for Bonus/Reward, - for Advance/Fine
            sign = 1 if adj.adjustment_type in ['Bonus', 'Reward'] else -1
            adjustments_net += sign * partial
        net_salary = latest_salary.salary_amount + adjustments_net - leave_deduction
        transaction = EmployeeSalaryTransaction(
            employee=employee,
            month=current_month,
            year=current_year,
            salary_amount=latest_salary.salary_amount,
            adjustments_net=adjustments_net,
            leave_days=days_absent,
            leave_deduction=leave_deduction,
            net_salary=net_salary,
            prepared_by=request.user
        )
        transaction.save()
        return JsonResponse({'status': 'success', 'message': 'Salary prepared'})
    return render(request, 'emp/prepare_salary_modal.html', {
        'employee': employee,
        'latest_salary': latest_salary,
        'pending_adjustments': pending_adjustments,
        'last_3_adjustments': last_3_adjustments,
        'last_3_salaries': last_3_salaries,
        'days_in_month': days_in_month,
        'default_absent': 2
    })
# endregion SALARY