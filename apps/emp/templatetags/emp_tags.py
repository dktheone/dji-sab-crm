from django import template
from apps.emp.models import Employee

register = template.Library()

@register.simple_tag
def get_employee_id(user):
    """Get employee ID for the logged-in user"""
    try:
        employee = Employee.objects.get(emp_code=user.username, status='Active')
        return employee.id
    except Employee.DoesNotExist:
        return None
