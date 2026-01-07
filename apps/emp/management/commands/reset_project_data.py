import os
import django
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django.conf import settings

# Import models
from apps.emp.models import (
    Department, Designation, Site, Contacts, Employee, 
    Attendance, Leave, DisciplinaryAction, Transfer, 
    TrainingRecord, MasterLog, EmployeeUpload,
    EmployeeSalaryMaster, EmployeeAdjustment, EmployeeSalaryTransaction,
    EmployeeAdjustmentMaster, EmployeeAdjustmentTransaction,
    LeaveType
)
from apps.leads.models import Lead, FollowUp, LeadConversionLog, LeadContact
from apps.vendors.models import Vendor, VendorDocument, VendorPayment, VendorRegistrationID

User = get_user_model()

class Command(BaseCommand):
    help = "Resets the database by clearing all project data, resetting sequences, and re-initializing the superuser."

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Full reset including Master Data (Departments, Designations, Sites, LeaveTypes).',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting Database Reset..."))
        
        full_reset = options['full']

        # List of models to clear (Order matters = reverse dependency)
        # 1. Transactional Data (Always clear)
        transactional_models = [
            # HRMS Transactions
            EmployeeSalaryTransaction,
            EmployeeAdjustmentTransaction,
            EmployeeAdjustment,
            EmployeeAdjustmentMaster,  # Also transaction-like master
            EmployeeSalaryMaster,      # Salary config
            Attendance, 
            Leave, 
            DisciplinaryAction, 
            Transfer, 
            TrainingRecord, 
            EmployeeUpload, 
            MasterLog,
            
            # Leads Transactions
            LeadConversionLog,
            FollowUp,
            LeadContact,
            
            # Vendors Transactions/Details
            VendorDocument,
            VendorPayment,
            VendorRegistrationID,
        ]

        # 2. Key Entities (Always clear)
        entity_models = [
            Lead,
            Vendor,
            Contacts,
            Employee,  # Employee is central
        ]

        # 3. Master Data (Optional - clear if --full is passed or just clear Site?)
        # User requested "RESET ... FOR USER, EMPLOYEES, HRMS, LEADS, AND VENDOR."
        # Usually Department/Designation are config, but if User wants a clean slate, 
        # let's assume Sites should definitely go because they are Client locations.
        # But Dept/Designation might be kept unless --full. 
        # HOWEVER, the prompt says "FIRST DELETE ALL RECORDS... FOR USER... EMPLOYEES... AND LEADS... AND VENDOR."
        # Sites are linked to Leads (Converted Site), so Sites must probably go or be handled carefully.
        # I will treat Site as Entity/Master that IS CLEARED because it's client data.
        
        master_models = [
            Site,
        ]

        if full_reset:
            master_models.extend([
                Department, 
                Designation,
                LeaveType
            ])
            # Note: I put placeholder above, correcting below.

        # Correct list building
        models_to_clear = []
        models_to_clear.extend(transactional_models)
        models_to_clear.extend(entity_models)
        models_to_clear.extend(master_models)
        
        if full_reset:
            models_to_clear.extend([Department, Designation, LeaveType])

        # EXECUTE DELETION
        self.stdout.write("Deleting records...")
        for model in models_to_clear:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                self.stdout.write(f"  - Deleted {count} {model.__name__} records")

        # Delete Users (Except maybe we want to delete ALL users as requested)
        self.stdout.write("Deleting Users...")
        User.objects.all().delete()
        self.stdout.write("  - Deleted all User records")

        # RESET SQLLITE SEQUENCES
        self.stdout.write("Resetting Auto-Increment Sequences...")
        # Get all table names for the models we cleared + auth_user
        tables_to_reset = [m._meta.db_table for m in models_to_clear]
        tables_to_reset.append('auth_user')
        tables_to_reset.append('auth_user_groups')
        tables_to_reset.append('auth_user_user_permissions')
        
        # Adding Groups/Permission tables if full reset? 
        # User said "USER" tables.
        # Let's just reset sequences for the models we touched.
        
        with connection.cursor() as cursor:
            # SQLite specific sequence reset
            if 'sqlite' in settings.DATABASES['default']['ENGINE']:
                for table in tables_to_reset:
                    try:
                        cursor.execute("DELETE FROM sqlite_sequence WHERE name=%s;", [table])
                    except Exception as e:
                        # Ignore if table not in sequence (maybe no auto-increment used yet)
                        pass
                self.stdout.write("  - SQLite sequences reset.")
            else:
                self.stdout.write(self.style.WARNING("  - Non-SQLite DB detected. Sequence reset might not work automatically."))

        # RE-CREATE SUPERUSER
        self.stdout.write("Creating Superuser...")
        username = "SAB0001"
        email = "info@sabhospitality.com"
        password = "ChangeMe123!" 

        if not User.objects.filter(username=username).exists():
            admin_user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Santosh',
                last_name='Chand'
            )
            self.stdout.write(self.style.SUCCESS(f"  - Superuser '{username}' created successfully"))
            
            # Force update emp_id via raw SQL since it's not in the model
            with connection.cursor() as cursor:
                cursor.execute("UPDATE auth_user SET emp_id = 1 WHERE username = %s", [username])
                self.stdout.write("  - Superuser emp_id set to 1 via Raw SQL")


        # RE-POPULATE MASTER DATA (Minimum required for system to operate)
        # Even if not --full, if we deleted Sites/Employees, we are good.
        # If we did --full, we deleted Depts. We should recreate them if --full is used?
        # The prompt implies a "Setup" phase follows. 
        # But to be safe, if we deleted Departments (via full) we should probably restore them.
        # However, the user said "THEN ADDING THE SUPER USER... IF IT IS PLANNED LIKE THIS...".
        # I will stick to just the requested steps.
        
        # If the user did NOT run with --full, Department/Designation are still there.
        # If they DID run with --full, they are gone.
        
        self.stdout.write(self.style.SUCCESS("\nRESET COMPLETE."))
        self.stdout.write("To re-populate initial data (Departments, Designations), run:")
        self.stdout.write(self.style.NOTICE("  python setup_complete_database.py"))
        
