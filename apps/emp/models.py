from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from apps.emp.utils import generate_random_key
from country_state_city import State, City
import os
# from apps import cdata 
# from apps.ops.models import Site


# Fetch states for India
STATES = State.get_states_of_country('IN')
STATE_CHOICES = [(state.iso_code, state.name) for state in STATES]    



GENRAL_STATUS_CHOICES = [
    ('Active', 'Active'),
    ('Inactive', 'Inactive')
]

GENDER_CHOICES = [    
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
]

NATIONALITY_CHOICES = [
    ('Indian', 'Indian'),
    ('Nepali', 'Nepali'),
    ('Other', 'Other'),
]

ID_CHOICES = [('Voter ID','Voter ID'), ('Driving Licence No.','Driving Licence No.'), ('International ID','International ID'), ('Other','Other')]




def get_photo_upload_path(instance, filename):
    """Generate upload path for Employee photo: media/{emp_code}/{emp_code}_{random_key}{ext}"""
    ext = os.path.splitext(filename)[1]
    random_key = generate_random_key()
    return os.path.join('Uploads', 'employees', instance.emp_code, f'{instance.emp_code}_{random_key}{ext}')

def get_file_upload_path(instance, filename):
    """Generate upload path for EmployeeUpload file: media/{emp_code}/{emp_code}_{random_key}{ext}"""
    ext = os.path.splitext(filename)[1]
    random_key = generate_random_key()
    # print(os.path.join('Uploads', 'employee_uploads', instance.employee.emp_code, f'{instance.employee.emp_code}_{random_key}{ext}'))
    return os.path.join('Uploads', 'employee_uploads', instance.employee.emp_code, f'{instance.employee.emp_code}_{random_key}{ext}')

class Department(models.Model):
    department_name = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=100, choices=GENRAL_STATUS_CHOICES, default='Active', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'departments'

    def __str__(self):
        return self.department_name

class Designation(models.Model):
    designation_name = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=100, choices=GENRAL_STATUS_CHOICES, default='Active', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'designations'

    def __str__(self):
        return self.designation_name

class LeaveType(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('CL', 'Casual Leave'),
        ('SL', 'Sick Leave'),
        ('EL', 'Earned Leave'),
    ]
    leave_type_code = models.CharField(max_length=2, choices=LEAVE_TYPE_CHOICES, unique=True)
    leave_type_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'leave_types'

    def __str__(self):
        return self.leave_type_name



class Site(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Under Maintenance', 'Under Maintenance'),
    ]
    site_name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, choices=STATE_CHOICES, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    contact1 = models.CharField(max_length=15, blank=True, null=True)
    contact2 = models.CharField(max_length=15, blank=True, null=True)
    email =  models.CharField(max_length=50, blank=True, null=True)
    website =  models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    remark = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'sites'

    def __str__(self):
        return self.site_name

class Contacts(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=100, choices=STATE_CHOICES, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    event_date = models.DateField(blank=True, null=True)
    event_date_remark = models.CharField(max_length=150, blank=True, null=True)
    contact1 = models.CharField(max_length=15)
    contact2 = models.CharField(max_length=15, blank=True, null=True)
    contact3 = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    designation = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=GENRAL_STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'contacts'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


#region Employee Details
class EmployeeStatus(models.TextChoices):
    # Employment Status
    INACTIVE = 'InActive', 'InActive'
    ACTIVE = 'Active', 'Active'
    TERMINATED = 'Terminated', 'Terminated'
    SUSPENDED = 'Suspended', 'Suspended'
    ON_LEAVE = 'On Leave', 'On Leave'
    
    # Leave Statuses
    LOA = 'Leave of Absence', 'Leave of Absence'
    MATERNITY_LEAVE = 'Maternity/Paternity Leave', 'Maternity/Paternity Leave'
    MEDICAL_LEAVE = 'Medical Leave', 'Medical Leave'
    SABBATICAL = 'Sabbatical', 'Sabbatical'
    
    # Hiring/Recruitment Status
    PRE_HIRE = 'Pre-Hire', 'Pre-Hire'
    ONBOARDING = 'Onboarding', 'Onboarding'
    PROBATION = 'Probation', 'Probation'
    
    # Special/Retired Statuses
    RETIRED = 'Retired', 'Retired'
    ARCHIVED = 'Archived', 'Archived'

class Employee(models.Model):
    emp_code = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50, blank=False, null=False)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    marital_status = models.CharField(
        max_length=50,
        choices=[('Single','Single'), ('Married','Married'), ('Divorced','Divorced'), ('Widowed','Widowed')],
        blank=True, null=True
    )
    blood_group = models.CharField(
        max_length=5,
        choices=[('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
                 ('O+','O+'),('O-','O-'),('AB+','AB+'),('AB-','AB-')],
        blank=True, null=True
    )
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE, null=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=False, default=1)
    site = models.ForeignKey(Site, blank=True, null=True, on_delete=models.CASCADE)
    dob = models.DateField()
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    contact_no = models.CharField(max_length=15)
    nationality = models.CharField(max_length=50, choices=NATIONALITY_CHOICES, default='Indian')
    
    cor_address = models.CharField(max_length=255, blank=True, null=True)
    cor_state = models.CharField(max_length=100, choices=STATE_CHOICES, blank=True, null=True)
    cor_city = models.CharField(max_length=100, blank=True, null=True)
    cor_pincode = models.CharField(max_length=10, blank=True, null=True)
    per_address = models.CharField(max_length=255, blank=True, null=True)
    per_state = models.CharField(max_length=100, choices=STATE_CHOICES, blank=True, null=True)
    per_city = models.CharField(max_length=100, blank=True, null=True)
    per_pincode = models.CharField(max_length=10, blank=True, null=True)
    
    photo = models.ImageField(upload_to=get_photo_upload_path, blank=True, null=True, default='nopic.jpg')
    joining_date = models.DateField()
    
    uan_no = models.CharField(max_length=20, blank=True, null=True)
    pf_esic_no = models.CharField(max_length=20, blank=True, null=True)

    passport_no = models.CharField(max_length=24, unique=True, blank=True, null=True)
    aadhaar_no = models.CharField(max_length=12, unique=True, blank=True, null=True)
    pan_card = models.CharField(max_length=10, unique=True, blank=True, null=True)    
    other_id_proof_type = models.CharField(max_length=50, blank=True, null=True, choices=ID_CHOICES)
    other_id_proof_no = models.CharField(max_length=50, blank=True, null=True)
    
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    emergency_person_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_relation = models.CharField(max_length=50, blank=True, null=True)
    emergency_alternative_no = models.CharField(max_length=15, blank=True, null=True)

    
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_no = models.CharField(max_length=50, unique=True, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True)    
    status = models.CharField(max_length=100, choices=EmployeeStatus.choices, default=EmployeeStatus.INACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'employees'
        constraints = [
            models.UniqueConstraint(
                fields=['aadhaar_no'],
                condition=models.Q(aadhaar_no__isnull=False) & ~models.Q(aadhaar_no=''),
                name='unique_non_empty_aadhaar_no'
            ),
            models.UniqueConstraint(
                fields=['pan_card'],
                condition=models.Q(pan_card__isnull=False) & ~models.Q(pan_card=''),
                name='unique_non_empty_pan_card'
            ),
            models.UniqueConstraint(
                fields=['passport_no'],
                condition=models.Q(passport_no__isnull=False) & ~models.Q(passport_no=''),
                name='unique_non_empty_passport_no'
            )
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.emp_code:
            # Generate emp_code (e.g., SAB0001)
            last_employee = Employee.objects.order_by('-id').first()
            if last_employee:
                last_id = int(last_employee.emp_code.replace('SAB', ''))
                new_id = last_id + 1
            else:
                new_id = 1
            self.emp_code = f'SAB{new_id:04d}'
        super().save(*args, **kwargs)
    
    def clean(self):
        super().clean()
        # Nationality-based validation for aadhaar_no and pan_card
        if self.nationality == 'Indian':
            if not self.aadhaar_no:
                raise ValidationError({'aadhaar_no': 'Aadhaar number is mandatory for Indian nationality.'})
            if not self.pan_card:
                raise ValidationError({'pan_card': 'PAN card is mandatory for Indian nationality.'})
        # Validate uniqueness for non-empty aadhaar_no and pan_card
        if self.aadhaar_no and Employee.objects.filter(aadhaar_no=self.aadhaar_no).exclude(id=self.id).exists():
            raise ValidationError({'aadhaar_no': 'An employee with this Aadhaar number already exists.'})
        if self.pan_card and Employee.objects.filter(pan_card=self.pan_card).exclude(id=self.id).exists():
            raise ValidationError({'pan_card': 'An employee with this PAN card already exists.'})
        if self.email and Employee.objects.filter(email=self.email).exclude(id=self.id).exists():
            raise ValidationError({'email': 'An employee with this email already exists.'})
        if self.account_no and Employee.objects.filter(account_no=self.account_no).exclude(id=self.id).exists():
            raise ValidationError({'account_no': 'An employee with this bank account number already exists.'})
        if self.upi_id and Employee.objects.filter(upi_id=self.upi_id).exclude(id=self.id).exists():
            raise ValidationError({'upi_id': 'An employee with this UPI ID already exists.'})

class EmployeeEducation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    degree = models.CharField(max_length=100)
    institution = models.CharField(max_length=255)
    passing_year = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'employee_education'

    def __str__(self):
        return f"{self.degree} from {self.institution} ({self.passing_year})"
    
class EmployeeExperience(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    reason_for_leaving = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'employee_experience'
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='check_end_date_gte_start_date'
            )
        ]

class EmployeeFamily(models.Model):
    RELATIONSHIP_CHOICES = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Spouse', 'Spouse'),
        ('Child', 'Child'),
        ('Sibling', 'Sibling'),
        ('Other', 'Other'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES)
    dob = models.DateField(blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    aadhaar_no = models.CharField(max_length=12, blank=True, null=True)
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'employee_family'

    def __str__(self):
        return f"{self.name} ({self.relationship})"    

class EmployeeUpload(models.Model):
    
    class DocumentType(models.TextChoices):
        AADHAAR = 'Aadhaar', _('Aadhaar')
        PAN = 'PAN', _('PAN')
        PASSPORT = 'Passport', _('Passport')
        DRIVING_LICENSE = 'Driving License', _('Driving License')
        VOTER_ID = 'Voter ID', _('Voter ID')
        REPORT = 'Report', _('Report')
        BILL = 'Bill', _('Bill')
        OTHER = 'Other', _('Other')
    
    class DocumentStatus(models.TextChoices):
        PENDING = 'Pending', _('Pending')
        APPROVED = 'Approved', _('Approved')
        REJECTED = 'Rejected', _('Rejected')
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50, choices=DocumentType.choices)
    file_path = models.FileField(upload_to=get_file_upload_path)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=DocumentStatus.choices, default=DocumentStatus.PENDING)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_by')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_uploads_created')
    class Meta:
        db_table = 'employee_uploads'
    def __str__(self):
        return f"{self.document_type} for {self.employee}"

"""
#region SALARY

class EmployeeSalaryMaster(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_masters')
    salary_amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    effective_from = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'employee_salary_master'
        ordering = ['-effective_from']
        unique_together = ['employee', 'effective_from']

    def __str__(self):
        return f"{self.employee} - {self.salary_amount} ({self.status})"

    def save(self, *args, **kwargs):
        if self.status == 'Active':
            # Deactivate other active records for the same employee
            EmployeeSalaryMaster.objects.filter(
                employee=self.employee, status='Active'
            ).exclude(id=self.id).update(status='Inactive')
        super().save(*args, **kwargs)

class EmployeeAdjustment(models.Model):
    ADJUSTMENT_TYPES = [
        ('Allowance', 'Allowance'),
        ('Deduction', 'Deduction'),
        ('Advance', 'Advance'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CLEARED', 'Cleared'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='adjustments')
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    date = models.DateField()
    remarks = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'employee_adjustments'
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee} - {self.adjustment_type} {self.amount}"

class EmployeeSalaryTransaction(models.Model):
    STATUS_CHOICES = [
        ('Prepared', 'Prepared'),
        ('Paid', 'Paid'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_transactions')
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField(validators=[MinValueValidator(1900)])
    salary_amount = models.DecimalField(max_digits=12, decimal_places=2)
    adjustments_net = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    leave_days = models.IntegerField(default=2, validators=[MinValueValidator(0)])
    leave_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Prepared')
    prepared_date = models.DateTimeField(auto_now_add=True)
    prepared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'employee_salary_transactions'
        unique_together = ['employee', 'month', 'year']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.employee} - {self.year}-{self.month:02d} ({self.net_salary})"

#endregion
""" 
#region SALARY
class EmployeeSalaryMaster(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_masters')
    salary_amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    effective_from = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'employee_salary_master'
        ordering = ['-effective_from']
        unique_together = ['employee', 'effective_from']

    def __str__(self):
        return f"{self.employee} - {self.salary_amount} ({self.status})"

    def save(self, *args, **kwargs):
        if self.status == 'Active':
            # Deactivate other active records for the same employee
            EmployeeSalaryMaster.objects.filter(
                employee=self.employee, status='Active'
            ).exclude(id=self.id).update(status='Inactive')
        super().save(*args, **kwargs)

class EmployeeAdjustment(models.Model):
    ADJUSTMENT_TYPES = [
        ('Advance', 'Advance'),
        ('Fine', 'Fine'),
        ('Bonus', 'Bonus'),
        ('Reward', 'Reward'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Partial', 'Partial'),
        ('Cleared', 'Cleared'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='adjustments')
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    date = models.DateField()
    remarks = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    remaining_amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'employee_adjustments'
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee} - {self.adjustment_type} {self.amount}"

    def save(self, *args, **kwargs):
        if not self.pk:  # On creation
            self.remaining_amount = self.amount
        if self.remaining_amount == 0:
            self.status = 'Cleared'
        elif self.remaining_amount < self.amount:
            self.status = 'Partial'
        else:
            self.status = 'Pending'
        super().save(*args, **kwargs)

# New Master-Transaction Architecture for Adjustments
class EmployeeAdjustmentMaster(models.Model):
    """
    Master record for employee adjustments (Advance/Fine/Bonus/Reward).
    This record contains the original adjustment details and never changes.
    """
    ADJUSTMENT_TYPES = [
        ('Advance', 'Advance'),
        ('Fine', 'Fine'),
        ('Bonus', 'Bonus'),
        ('Reward', 'Reward'),
    ]
    STATUS_CHOICES = [
        ('Active', 'Active'),      # Has outstanding balance
        ('Closed', 'Closed'),      # Fully settled
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='adjustment_masters')
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    cleared_amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )  # Track settled amount directly
    date_issued = models.DateField()
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'employee_adjustment_masters'
        ordering = ['-date_issued']
    
    def __str__(self):
        return f"{self.employee} - {self.adjustment_type} ₹{self.total_amount}"
    
    @property
    def settled_amount(self):
        """Alias for cleared_amount for backward compatibility"""
        return self.cleared_amount
    
    @property
    def outstanding_amount(self):
        """Calculate remaining outstanding amount"""
        return self.total_amount - self.cleared_amount
    
    def is_fully_settled(self):
        """Check if adjustment is fully settled"""
        return self.outstanding_amount <= Decimal('0')


class EmployeeAdjustmentTransaction(models.Model):
    """
    Transaction record for each adjustment settlement.
    Records when and how much was settled from salary.
    """
    TRANSACTION_TYPES = [
        ('Full', 'Full Settlement'),
        ('Partial', 'Partial Settlement'),
    ]
    
    adjustment_master = models.ForeignKey(
        EmployeeAdjustmentMaster, 
        on_delete=models.CASCADE, 
        related_name='adjustment_transactions'
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Denormalized for easy queries
    settlement_amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    settlement_date = models.DateField(auto_now_add=True)
    salary_month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    salary_year = models.IntegerField(validators=[MinValueValidator(1900)])
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'employee_adjustment_transactions'
        ordering = ['-salary_year', '-salary_month', '-settlement_date']
    
    def __str__(self):
        return f"{self.adjustment_master.adjustment_type} - ₹{self.settlement_amount} ({self.salary_month}/{self.salary_year})"


class EmployeeSalaryTransaction(models.Model):
    STATUS_CHOICES = [
        ('Prepared', 'Prepared'),
        ('Paid', 'Paid'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_transactions')
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField(validators=[MinValueValidator(1900)])
    salary_amount = models.DecimalField(max_digits=12, decimal_places=2)
    adjustments_net = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    leave_days = models.IntegerField(default=2, validators=[MinValueValidator(0)])
    leave_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Prepared')
    prepared_date = models.DateTimeField(auto_now_add=True)
    prepared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)

    @property
    def month_name(self):
        import calendar
        return calendar.month_name[self.month]
    
    @property
    def total_days(self):
        import calendar
        return calendar.monthrange(self.year, self.month)[1]
    
    @property
    def present_days(self):
        # Taking default 0 for leave_days if None
        leaves = self.leave_days if self.leave_days else 0
        return self.total_days - leaves

    class Meta:
        db_table = 'employee_salary_transactions'
        unique_together = ['employee', 'month', 'year']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.employee} - {self.year}-{self.month:02d} ({self.net_salary})"

#endregion

#endregion

class Attendance(models.Model):
    SHIFT_CHOICES = [
        ('Morning', 'Morning'),
        ('Evening', 'Evening'),
        ('Night', 'Night'),
    ]
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    attendance_date = models.DateField()
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.SET_NULL, null=True, blank=True)
    overtime_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'attendance'
        unique_together = ('employee', 'attendance_date')

class Payroll(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    salary_month = models.DateField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    advance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'payroll'
        unique_together = ('employee', 'salary_month')

class Leave(models.Model):
    STATUS_CHOICES = [
        ('Approved', 'Approved'),
        ('Pending', 'Pending'),
        ('Rejected', 'Rejected'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField()
    no_of_days = models.IntegerField()
    approved_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='approved_leaves')
    remarks = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Approved')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'leaves'
        constraints = [
            models.CheckConstraint(check=models.Q(to_date__gte=models.F('from_date')), name='check_to_date_gte_from_date')
        ]

class DisciplinaryAction(models.Model):
    ACTION_TYPE_CHOICES = [
        ('Warning', 'Warning'),
        ('Fine', 'Fine'),
        ('Exit', 'Exit'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES)
    reason = models.TextField()
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    action_taken = models.CharField(max_length=255)
    action_date = models.DateField()
    approved_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='approved_actions')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'disciplinary_actions'

class Transfer(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    from_site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='transfers_from')
    to_site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='transfers_to')
    transfer_date = models.DateField()
    reason = models.TextField()
    approved_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='approved_transfers')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'transfers'

class TrainingRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    training_topic = models.CharField(max_length=255)
    conducted_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='conducted_trainings')
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    training_date = models.DateField()
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'training_records'

class MasterLog(models.Model):
    table_name = models.CharField(max_length=100)
    record_id = models.IntegerField()
    old_data = models.JSONField()
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'master_log'
        
    