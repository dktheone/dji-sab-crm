from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.emp.models import Department, Designation, Site, Contact, Employee, Payroll, EmployeeUpload, Attendance, Leave, DisciplinaryAction, Transfer, TrainingRecord, MasterLog

# Create groups
admin_group, _ = Group.objects.get_or_create(name='admin')
hr_group, _ = Group.objects.get_or_create(name='hr')
employee_group, _ = Group.objects.get_or_create(name='employee')

# Define permissions for each model
models = [Department, Designation, Site, Contact, Employee, Payroll, EmployeeUpload, Attendance, Leave, DisciplinaryAction, Transfer, TrainingRecord, MasterLog]
for model in models:
    content_type = ContentType.objects.get_for_model(model)
    # Admin: Full permissions
    for perm in ['add', 'change', 'delete', 'view']:
        permission = Permission.objects.get(codename=f'{perm}_{model.__name__.lower()}', content_type=content_type)
        admin_group.permissions.add(permission)
    # HR: Add, change, view (no delete, no employee approval)
    for perm in ['add', 'change', 'view']:
        permission = Permission.objects.get(codename=f'{perm}_{model.__name__.lower()}', content_type=content_type)
        hr_group.permissions.add(permission)
    # Employee: Limited permissions
    if model in [Employee, Attendance, Leave, Site, Contact]:
        for perm in ['change', 'view'] if model == Employee else ['add', 'view']:
            permission = Permission.objects.get(codename=f'{perm}_{model.__name__.lower()}', content_type=content_type)
            employee_group.permissions.add(permission)