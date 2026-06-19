from django.test import TestCase
from django.urls import reverse
from apps.emp.utils import get_log_classifications
from apps.emp.views import EmployeeDashboardView

class EmployeeAppTests(TestCase):
    def test_log_classifications_loaded(self):
        """Test that log classifications are successfully loaded from JSON."""
        classifications = get_log_classifications()
        self.assertIsInstance(classifications, dict)
        self.assertIn("Profile", classifications)
        self.assertEqual(classifications["Profile"]["icon"], "fas fa-user-edit")
        self.assertEqual(classifications["Profile"]["bg_class"], "bg-info")

    def test_dashboard_pagination_disabled(self):
        """Test that EmployeeDashboardView has pagination disabled (paginate_by is None or not set)."""
        paginate_by = getattr(EmployeeDashboardView, 'paginate_by', None)
        self.assertIsNone(paginate_by)

    def test_salary_master_list_view_annotated_queryset(self):
        """Test that the salary_master_list view queryset is annotated with active salary details."""
        from django.contrib.auth.models import User
        from apps.emp.models import Employee, EmployeeSalaryMaster, Department, Designation, Site
        import datetime

        # Create user for authentication
        user = User.objects.create_user(username='hr_user', password='password')
        # Assign user to 'hr' group to bypass role_required decorator
        from django.contrib.auth.models import Group
        hr_group, _ = Group.objects.get_or_create(name='hr')
        user.groups.add(hr_group)

        # Log in
        self.client.login(username='hr_user', password='password')

        # Create department, designation and site
        dept = Department.objects.create(department_name="Test Dept", status="Active", created_by=user)
        desig = Designation.objects.create(designation_name="Test Desig", created_by=user)
        site = Site.objects.create(site_name="Test Site", status="Active", created_by=user)

        # Create mock employee
        emp = Employee.objects.create(
            first_name="John",
            last_name="Doe",
            emp_code="EMP999",
            status="Active",
            department=dept,
            designation=desig,
            site=site,
            joining_date=datetime.date.today(),
            dob=datetime.date(1990, 1, 1),
            gender="Male",
            blood_group="O+",
            marital_status="Single",
            contact_no="1234567890",
            email="john.doe@example.com",
            created_by=user
        )

        # Create mock active salary master
        salary = EmployeeSalaryMaster.objects.create(
            employee=emp,
            salary_amount=50000.00,
            effective_from=datetime.date.today(),
            status="Active",
            remarks="Initial Salary",
            created_by=user
        )

        # Request salary master list page
        response = self.client.get(reverse('apps.emp:salary_master_list'))
        self.assertEqual(response.status_code, 200)

        # Verify that context contains annotated employees and our John Doe has correct salary annotations
        employees = response.context['employees']
        john_doe_annotated = None
        for e in employees:
            if e.id == emp.id:
                john_doe_annotated = e
                break

        self.assertIsNotNone(john_doe_annotated)
        # Check annotations
        self.assertEqual(float(john_doe_annotated.active_salary_amount), 50000.00)
        self.assertEqual(john_doe_annotated.active_salary_effective, datetime.date.today())
        self.assertEqual(john_doe_annotated.active_salary_remarks, "Initial Salary")
        self.assertEqual(john_doe_annotated.active_salary_id, salary.id)

        # Assert filter models are present in response context
        self.assertIn('departments', response.context)
        self.assertIn('designations', response.context)
        self.assertIn('sites', response.context)

        # Check departments, designations, and sites list content
        self.assertTrue(response.context['departments'].filter(id=dept.id).exists())
        self.assertTrue(response.context['designations'].filter(id=desig.id).exists())
        self.assertTrue(response.context['sites'].filter(id=site.id).exists())

    def test_dashboard_contains_site_summaries(self):
        """Test that the dashboard view context contains site_summaries with correct formatting."""
        from django.contrib.auth.models import User
        from apps.emp.models import Employee, Department, Designation, Site
        import datetime

        user = User.objects.create_user(username='hr_user_db', password='password')
        self.client.login(username='hr_user_db', password='password')

        dept = Department.objects.create(department_name="HR Dept", status="Active", created_by=user)
        desig = Designation.objects.create(designation_name="HR Officer", created_by=user)
        site = Site.objects.create(site_name="Metro Hospital", status="Active", address="123 Street", city="Cityville", created_by=user)

        Employee.objects.create(
            first_name="Jane",
            last_name="Doe",
            emp_code="hr_user_db",
            status="Active",
            department=dept,
            designation=desig,
            site=site,
            joining_date=datetime.date.today(),
            dob=datetime.date(1990, 1, 1),
            gender="Female",
            blood_group="O+",
            marital_status="Single",
            contact_no="1234567890",
            email="jane.doe@example.com",
            created_by=user
        )

        response = self.client.get(reverse('apps.emp:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('site_summaries', response.context)
        
        # Check site summaries content
        summaries = response.context['site_summaries']
        self.assertEqual(len(summaries), 1)
        self.assertEqual(summaries[0]['name'], "Metro Hospital")
        self.assertEqual(summaries[0]['address'], "123 Street, Cityville")
        self.assertEqual(summaries[0]['employee_count'], 1)
        self.assertIn("• HR Dept / HR Officer: 1", summaries[0]['tooltip'])

