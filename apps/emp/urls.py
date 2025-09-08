# from django.urls import path
# from apps.emp import views as emp_views
# from apps.pages import views as page_view
# from django.views.generic import RedirectView




# app_name = 'apps.emp'  # Namespace for URLs

# urlpatterns = [
#     path('dashboard/', emp_views.dashboard, name='dashboard'),    
#     path('departments/', emp_views.department_crud, name='department_crud'),
#     path('departments/delete/<int:department_id>/', emp_views.delete_department, name='delete_department'),
#     path('designations/', emp_views.designation_crud, name='designation_crud'),
#     path('designations/delete/<int:designation_id>/', emp_views.delete_designation, name='delete_designation'),
    
#     path('sites/', emp_views.site_crud, name='site_crud'),
#     path('sites/delete/<int:site_id>/', emp_views.delete_site, name='delete_site'),
    
#     # path('sites/crud/', emp_views.site_crud, name='site_crud'),
#     # path('sites/delete/<int:site_id>/', emp_views.delete_site, name='delete_site'),
    
    
#     path('employees/list/', emp_views.employee_list, name='employee_list'),
#     # path('employees/dashboard/', emp_views.EmployeeDashboardView,  name='employee_dashboard'),
#     # Replace or keep existing employee_list if needed
#     path('employees/dash/', emp_views.EmployeeDashboardView.as_view(), name='employee_dash'),
    
    
#     path('employees/add/', emp_views.employee_form, name='employee_form'),
#     path('employees/details/<int:employee_id>', emp_views.employee_additional, name='employee_details'),
#     path('employees/edit/<int:employee_id>/', emp_views.employee_form, name='employee_edit'),
#     path('employees/upload/<int:employee_id>/', emp_views.employee_uploads, name='employee_uploads'),
    
#     path('employees/view/<int:employee_id>/', emp_views.employee_view, name='employee_view'),
#     path('employees/status/<int:employee_id>/', emp_views.update_employee_status, name='update_employee_status'),
#     path('employees/get-cities/', emp_views.get_cities, name='get_cities'),
    
#     path('employees/create-user/', emp_views.create_employee_user, name='create_employee_user'),
#     path('get-ifsc-data/', emp_views.get_ifsc_data, name='get_ifsc_data'),
    
    
#     # Salary Master URLs
#     path('salary-master/', emp_views.salary_master_list, name='salary_master_list'),
#     path('salary-master/<int:employee_id>/', emp_views.salary_master_form, name='salary_master_form'),
    
#     # Employee Adjustments URLs
#     path('adjustments/', emp_views.adjustments_list, name='adjustments_list'),
#     path('adjustments/<int:employee_id>/', emp_views.adjustments_form, name='adjustments_form'),
    
#     # Salary Preparation URLs
#     path('salary-preparation/', emp_views.salary_preparation, name='salary_preparation'),
#     path('make-salary/<int:employee_id>/', emp_views.make_salary, name='make_salary'),

# ]


from django.urls import path
from apps.emp import views as emp_views
from django.views.generic import RedirectView

app_name = 'apps.emp'

urlpatterns = [
    
    path('dashboard/', emp_views.dashboard, name='dashboard'),
    path('departments/', emp_views.department_crud, name='department_crud'),
    path('departments/delete/<int:department_id>/', emp_views.delete_department, name='delete_department'),
    path('designations/', emp_views.designation_crud, name='designation_crud'),
    path('designations/delete/<int:designation_id>/', emp_views.delete_designation, name='delete_designation'),
    path('sites/', emp_views.site_crud, name='site_crud'),
    path('sites/delete/<int:site_id>/', emp_views.delete_site, name='delete_site'),
    
    
    path('list/', emp_views.employee_list, name='employee_list'),
    path('dash/', emp_views.EmployeeDashboardView.as_view(), name='employee_dash'),

    path('add/', emp_views.employee_form, name='employee_form'),
    path('details/<int:employee_id>', emp_views.employee_additional, name='employee_details'),
    path('upload/<int:employee_id>/', emp_views.employee_uploads, name='employee_uploads'),
    path('edit/<int:employee_id>/', emp_views.employee_form, name='employee_edit'),
    # path('employees/list/', emp_views.employee_list, name='employee_list'),
    path('view/<int:employee_id>/', emp_views.employee_view, name='employee_view'),
    path('status/<int:employee_id>/', emp_views.update_employee_status, name='update_employee_status'),
    path('get-cities/', emp_views.get_cities, name='get_cities'),
    path('create-user/', emp_views.create_employee_user, name='create_employee_user'),
    # New URLs
    path('salary-master/', emp_views.salary_master_list, name='salary_master_list'),
    path('salary-master/<int:emp_id>/', emp_views.salary_master_detail, name='salary_master_detail'),
    path('adjustments/', emp_views.adjustments_page, name='adjustments_page'),
    
    path('adjustments2/', emp_views.adjustments_list, name='adjustments_list'),
    path('adjustments_form/', emp_views.adjustments_form, name='adjustments_form'),
    path('salary-preparation/', emp_views.salary_preparation, name='salary_preparation'),
    path('prepare-salary/<int:emp_id>/', emp_views.prepare_salary, name='prepare_salary'),
]