import os
import django
from django.db.models import Count

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.emp.models import EmployeeSalaryTransaction, Employee

def inspect_salary_status():
    print("--- Salary Transaction Summary by Month ---")
    stats = EmployeeSalaryTransaction.objects.values('month', 'year', 'status').annotate(count=Count('id')).order_by('year', 'month')
    
    for stat in stats:
        print(f"{stat['month']}/{stat['year']} - Status: {stat['status']}, Count: {stat['count']}")

    print("\n--- Active Employees Count ---")
    active_count = Employee.objects.filter(status='Active').count()
    print(f"Total Active Employees: {active_count}")

if __name__ == '__main__':
    inspect_salary_status()
