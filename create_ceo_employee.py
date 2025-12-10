import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.emp.models import Department, Designation, Employee

User = get_user_model()

# Get admin user
admin_user = User.objects.get(username='admin')

# Create Department if not exists
department, created = Department.objects.get_or_create(
    department_name='Management',
    defaults={
        'status': 'Active',
        'created_by': admin_user
    }
)
if created:
    print(f"[+] Created Department: {department.department_name}")
else:
    print(f"[+] Department already exists: {department.department_name}")

# Create Designation if not exists
designation, created = Designation.objects.get_or_create(
    designation_name='CEO',
    defaults={
        'status': 'Active',
        'created_by': admin_user
    }
)
if created:
    print(f"[+] Created Designation: {designation.designation_name}")
else:
    print(f"[+] Designation already exists: {designation.designation_name}")

# Create Employee for admin user
try:
    employee = Employee.objects.create(
        first_name='Santosh',
        last_name='Chand',
        designation=designation,
        department=department,
        dob=date(1990, 1, 1),  # Default DOB, can be updated later
        gender='Male',
        email='admin@sab.com',
        contact_no='9999999999',  # Default, can be updated later
        nationality='Indian',
        joining_date=date.today(),
        aadhaar_no='999999999999',  # Placeholder, should be updated
        pan_card='ABCDE1234F',  # Placeholder, should be updated
        status='Active',
        created_by=admin_user
    )
    print(f"[+] Created Employee: {employee.emp_code} - {employee.first_name} {employee.last_name}")
    print(f"    Designation: {employee.designation}")
    print(f"    Department: {employee.department}")
    print(f"    Status: {employee.status}")
except Exception as e:
    print(f"[-] Error creating employee: {str(e)}")
