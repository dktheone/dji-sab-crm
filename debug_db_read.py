import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.emp.models import EmployeeAdjustmentMaster, EmployeeAdjustmentTransaction, EmployeeSalaryTransaction

def print_separator(title):
    print(f"\n{'='*20} {title} {'='*20}")

def read_records():
    # 1. EmployeeAdjustmentMaster
    print_separator("EmployeeAdjustmentMaster (Latest 5)")
    masters = EmployeeAdjustmentMaster.objects.all().order_by('-id')[:5]
    if not masters:
        print("No records found.")
    for m in masters:
        print(f"ID: {m.id} | Emp: {m.employee.first_name} | Type: {m.adjustment_type} | "
              f"Total: {m.total_amount} | Cleared: {m.cleared_amount} | Status: {m.status}")

    # 2. EmployeeAdjustmentTransaction
    print_separator("EmployeeAdjustmentTransaction (Latest 5)")
    transactions = EmployeeAdjustmentTransaction.objects.all().order_by('-id')[:5]
    if not transactions:
        print("No records found.")
    for t in transactions:
        print(f"ID: {t.id} | Master ID: {t.adjustment_master.id} | Amount: {t.settlement_amount} | "
              f"Month/Year: {t.salary_month}/{t.salary_year} | Type: {t.transaction_type}")

    # 3. EmployeeSalaryTransaction
    print_separator("EmployeeSalaryTransaction (Latest 5)")
    salaries = EmployeeSalaryTransaction.objects.all().order_by('-id')[:5]
    if not salaries:
        print("No records found.")
    for s in salaries:
        print(f"ID: {s.id} | Emp: {s.employee.first_name} | Net Salary: {s.net_salary} | "
              f"Month/Year: {s.month}/{s.year} | Adj Net: {s.adjustments_net}")

if __name__ == "__main__":
    read_records()
