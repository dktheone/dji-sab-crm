import os
import django
from django.db.models import Count, Q, Case, When, Value, CharField
from django.utils import timezone
from dateutil.relativedelta import relativedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.emp.models import Employee, EmployeeSalaryMaster
from django.contrib.auth.models import User

def check_duplicate_active_masters():
    print("\n--- Checking for Duplicate Active Salary Masters ---")
    
    dupes = EmployeeSalaryMaster.objects.filter(status='Active').values('employee').annotate(
        active_count=Count('id')
    ).filter(active_count__gt=1)
    
    if dupes.exists():
        print(f"FOUND DUPLICATES: {dupes.count()} employees have multiple active salary masters!")
        for d in dupes:
            emp = Employee.objects.get(id=d['employee'])
            print(f"- Employee: {emp} (ID: {emp.id}) has {d['active_count']} active records.")
            
            masters = EmployeeSalaryMaster.objects.filter(employee=emp, status='Active')
            for m in masters:
                print(f"  > Master ID: {m.id}, Effective: {m.effective_from}, Status: {m.status}")
    else:
        print("No duplicate active salary masters found. Logic seems safe.")

def check_dashboard_query():
    print("\n--- Checking Dashboard Query ---")
    
    today = timezone.now()
    prev_month = today - relativedelta(months=1)
    check_month = prev_month.month
    check_year = prev_month.year

    queryset = Employee.objects.filter(status__in=['Active', 'Onboarding', 'Probation'])
    
    # Simulate Annotation
    queryset = queryset.annotate(
        salary_status=Case(
            When(salary_masters__status='Active', salary_masters__effective_from__lte=timezone.now(),
                 then=Value('Assigned')),
            default=Value('Pending'),
            output_field=CharField()
        )
    ).distinct()
    
    count = queryset.count()
    real_len = len(list(queryset))
    
    print(f"Dashboard Query .count(): {count}")
    print(f"Dashboard Query len(): {real_len}")
    
    if count != real_len:
        print("MISMATCH! .count() differs from len(). This implies duplication in SQL result set processing.")
    
    # Check if any employee appears twice in list
    ids = [e.id for e in queryset]
    unique_ids = set(ids)
    if len(ids) != len(unique_ids):
        print(f"DUPLICATION IN LIST! Total: {len(ids)}, Unique: {len(unique_ids)}")
    else:
        print("No duplication in resulting ID list.")

def check_salary_master_list_query():
    print("\n--- Checking Salary Master List Query (With Fix) ---")
    from django.db.models import Max, F
    
    # Simulate the query from salary_master_list view (WITH DISTINCT)
    with_salary_employees = Employee.objects.filter(status='Active').annotate(
        latest_salary=Max('salary_masters__effective_from')
    ).filter(salary_masters__effective_from=F('latest_salary'), salary_masters__status='Active').prefetch_related('salary_masters').distinct()

    count = with_salary_employees.count()
    real_len = len(list(with_salary_employees))
    
    print(f"Salary List Query .count(): {count}")
    print(f"Salary List Query len(): {real_len}")
    
    if count > 1: # Assuming 1 employee with 2 active records
        print("FAILURE: Salary Master List Query STILL produces DUPLICATES!")
    else:
        print("SUCCESS: Salary Master List Query handles duplicates correctly.")

if __name__ == "__main__":
    from datetime import date
    
    print("\n--- TEST 1: Model Save Logic ---")
    # Get CEO (SAB0001)
    emp = Employee.objects.filter(emp_code='SAB0001').first()
    if not emp:
        print("CEO Not Found! Running setup...")
        # (Assuming setup ran, but just in case)
        exit()

    # Clear existing
    EmployeeSalaryMaster.objects.filter(employee=emp).delete()
    
    # Create 1st Master
    m1 = EmployeeSalaryMaster.objects.create(
        employee=emp, 
        salary_amount=50000, 
        effective_from=date(2024, 1, 1),
        status='Active'
    )
    print(f"Created M1 (Active). ID: {m1.id}")
    
    # Create 2nd Master
    m2 = EmployeeSalaryMaster.objects.create(
        employee=emp, 
        salary_amount=60000, 
        effective_from=date(2024, 6, 1),
        status='Active'
    )
    print(f"Created M2 (Active). ID: {m2.id}")
    
    # Check M1 status
    m1.refresh_from_db()
    print(f"Checked M1 Status: {m1.status} (Expected: Inactive)")
    
    if m1.status == 'Inactive':
        print("SUCCESS: Save logic correctly deactivated old record.")
    else:
        print("FAILURE: Old record remained Active!")

    print("\n--- TEST 2: Forced Duplication & Query Check ---")
    # Force M1 back to Active
    EmployeeSalaryMaster.objects.filter(id=m1.id).update(status='Active')
    print("Forced M1 to Active. Now we have 2 Active records.")
    
    check_duplicate_active_masters()
    check_dashboard_query()
    check_salary_master_list_query()
    
    # Cleanup
    EmployeeSalaryMaster.objects.filter(employee=emp).delete()
    print("\n--- Cleanup Complete ---")
