import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.emp.models import (
    Department, Designation, Site, Contacts, Employee, Payroll, 
    EmployeeUpload, Attendance, Leave, DisciplinaryAction, 
    Transfer, TrainingRecord, MasterLog
)
from apps.leads.models import Lead

User = get_user_model()

print("=" * 60)
print("SAB CRM - Complete Database Setup")
print("=" * 60)

# ============================================================
# STEP 1: Create or Get Admin User
# ============================================================
print(f"\n[1] Setting up Admin User...")

User = get_user_model()

# Create or get admin user
admin_user, created = User.objects.get_or_create(
    username='SAB0001',
    defaults={
        'email': 'info@sabhospitality.com',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
        'first_name': 'Santosh',
        'last_name': 'Chand',
        'emp_id': 1  # Setup assumption: First employee
    }
)

if created:
    admin_user.set_password('ChangeMe123!')
    admin_user.save()
    print(f"   [+] Created Admin User: {admin_user.username} (Emp ID: 1)")
else:
    print(f"   [*] Admin User Exists: {admin_user.username}")
    
# Force update emp_id via raw SQL since it's not in the model
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("UPDATE auth_user SET emp_id = 1, first_name = 'Santosh', last_name = 'Chand' WHERE username = %s", [admin_user.username])
    print(f"   [+] Updated Admin User with Emp ID 1, First/Last Name (Raw SQL)")

# Ensure admin has superuser status
if not admin_user.is_superuser:
    admin_user.is_superuser = True
    admin_user.is_staff = True
    admin_user.save()
    print(f"   [+] Updated Admin User with superuser status")

# ============================================================
# STEP 1: Create Groups and Permissions
# ============================================================
print("\n[2] Setting up Groups and Permissions...")

# Create groups
admin_group, created = Group.objects.get_or_create(name='admin')
print(f"   {'[+] Created' if created else '[*] Exists'}: Admin Group")

hr_group, created = Group.objects.get_or_create(name='hr')
print(f"   {'[+] Created' if created else '[*] Exists'}: HR Group")

employee_group, created = Group.objects.get_or_create(name='employee')
print(f"   {'[+] Created' if created else '[*] Exists'}: Employee Group")

# Define models for permissions
models = [
    Department, Designation, Site, Contacts, Employee, Payroll, 
    EmployeeUpload, Attendance, Leave, DisciplinaryAction, 
    Transfer, TrainingRecord, MasterLog, Lead
]

print(f"\n[3] Assigning Permissions to Groups...")

for model in models:
    content_type = ContentType.objects.get_for_model(model)
    
    # Admin: Full permissions (add, change, delete, view)
    for perm in ['add', 'change', 'delete', 'view']:
        try:
            permission = Permission.objects.get(
                codename=f'{perm}_{model.__name__.lower()}', 
                content_type=content_type
            )
            admin_group.permissions.add(permission)
        except Permission.DoesNotExist:
            print(f"   [!] Permission not found: {perm}_{model.__name__.lower()}")
    
    # HR: Add, change, view (no delete)
    for perm in ['add', 'change', 'view']:
        try:
            permission = Permission.objects.get(
                codename=f'{perm}_{model.__name__.lower()}', 
                content_type=content_type
            )
            hr_group.permissions.add(permission)
        except Permission.DoesNotExist:
            pass
    
    # Employee: Limited permissions
    if model in [Employee, Attendance, Leave, Site, Contacts]:
        perms = ['change', 'view'] if model == Employee else ['add', 'view']
        for perm in perms:
            try:
                permission = Permission.objects.get(
                    codename=f'{perm}_{model.__name__.lower()}', 
                    content_type=content_type
                )
                employee_group.permissions.add(permission)
            except Permission.DoesNotExist:
                pass

print(f"   [+] Admin Group: {admin_group.permissions.count()} permissions")
print(f"   [+] HR Group: {hr_group.permissions.count()} permissions")
print(f"   [+] Employee Group: {employee_group.permissions.count()} permissions")

# Assign admin user to admin group
admin_user.groups.add(admin_group)
admin_user.is_staff = True
admin_user.is_superuser = True
admin_user.save()
print(f"\n[4] Assigned Admin User to Admin Group with full access")

# ============================================================
# STEP 2: Create Departments
# ============================================================
print(f"\n[5] Creating Departments...")

departments_list = [
    'Administration',
    'Accounts',
    'HR',
    'Sales & Marketing',
    'Purchase',
    'Management'  # Already exists from previous setup
]

departments_created = []
for dept_name in departments_list:
    dept, created = Department.objects.get_or_create(
        department_name=dept_name,
        defaults={
            'status': 'Active',
            'created_by': admin_user
        }
    )
    departments_created.append(dept)
    print(f"   {'[+] Created' if created else '[*] Exists'}: {dept_name}")

# ============================================================
# STEP 3: Create Designations
# ============================================================
print(f"\n[6] Creating Designations...")

designations_list = [
    'CEO',
    'HR Manager',
    'Managing Partner',
    'Executive Chef',
    'Manager',
    'Sales Head',
    'Sales Executive',
    'Accounts Head',
    'Purchasing Manager'
]

designations_created = []
for desig_name in designations_list:
    desig, created = Designation.objects.get_or_create(
        designation_name=desig_name,
        defaults={
            'status': 'Active',
            'created_by': admin_user
        }
    )
    designations_created.append(desig)
    print(f"   {'[+] Created' if created else '[*] Exists'}: {desig_name}")

# ============================================================
# STEP 4: Create CEO Employee
# ============================================================
print(f"\n[7] Creating/Verifying CEO Employee Record...")

try:
    ceo_department = Department.objects.get(department_name='Administration')
    ceo_designation = Designation.objects.get(designation_name='CEO')
    
    ceo_employee, created = Employee.objects.get_or_create(
        emp_code='SAB0001',
        defaults={
            'first_name': 'Santosh',
            'last_name': 'Chand',
            'designation': ceo_designation,
            'department': ceo_department,
            'joining_date': date(2015, 1, 1),
            'dob': date(1990, 5, 10),
            'email': 'info@sabhospitality.com',
            'contact_no': '9839374447',
            'status': 'Active',
            'created_by': admin_user
        }
    )
    
    if created:
        print(f"   [+] Created CEO Employee: {ceo_employee.first_name} {ceo_employee.last_name} ({ceo_employee.emp_code})")
    else:
        print(f"   [*] CEO Employee Exists: {ceo_employee.first_name} {ceo_employee.last_name}")

except Exception as e:
    print(f"   [!] Error creating CEO Employee: {e}")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 60)
print("SETUP COMPLETE - Summary")
print("=" * 60)
print(f"Users:        {User.objects.count()}")
print(f"Groups:       {Group.objects.count()}")
print(f"Departments:  {Department.objects.count()}")
print(f"Designations: {Designation.objects.count()}")
print(f"Employees:    {Employee.objects.count()}")
print(f"Leads:        {Lead.objects.count()}")
print("=" * 60)
print("\nAdmin user has full access to all modules!")
print("Dashboard should now work correctly.\n")
