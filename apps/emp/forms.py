from django import forms
# from apps.emp.models import Department, Designation, Employee, EmployeeUpload, Site, CustomUser
from apps.emp.models import Department, Designation, Site, Contacts
from apps.emp.models import Employee, EmployeeEducation, EmployeeExperience, EmployeeFamily, EmployeeUpload, EmployeeSalaryMaster, EmployeeAdjustment, EmployeeSalaryTransaction

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, HTML, ButtonHolder, BaseInput, Field, Div
from django_select2.forms import Select2Widget
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.templatetags.static import static


# from django_select2 import forms as s2forms
# class DepartmentWidget(s2forms.ModelSelect2Widget):
#     search_fields = [
#         "department_name__icontains"
#     ]
    
# class DepartmentForm(forms.ModelForm):
#     class Meta:
#         model = Department
#         fields = ['department_name', 'status']

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['department_name', 'status']
        widgets = {
            'status': forms.Select()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(Field('department_name'), css_class='col-md-6'),
                Column(Field('status'), css_class='col-md-4')
            )
        )
                
# class DesignationForm(forms.ModelForm):
#     class Meta:
#         model = Designation
#         fields = ['designation_name', 'status']

class DesignationForm(forms.ModelForm):
    class Meta:
        model = Designation
        fields = ['designation_name', 'status']
        widgets = {
            'status': forms.Select()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(Field('designation_name'), css_class='col-md-6'),
                Column(Field('status'), css_class='col-md-4')
            )
        )

class SitesForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['site_name', 'address', 'contact1', 'contact2', 'website', 'email', 'city', 'state', 'pincode', 'status', 'remark']
        widgets = {
            'state':  Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
            'city':   Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
            'status': Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # We'll handle form tag in template
        self.helper.layout = Layout(
            Row(
                Column(Field('site_name'), css_class='form-group myinput col-md-12 mb-0')
            ),
            Row(
                Column(Field('contact1'), css_class='form-group myinput col-md-6 mb-0'),
                Column(Field('contact2'), css_class='form-group myinput col-md-6')
            ),
            Row(
                Column(Field('email'), css_class='form-group myinput col-md-6 mb-0'),
                Column(Field('website'), css_class='form-group myinput col-md-6')
            ),
            Row(
                Column(Field('address'), css_class='form-group myinput col-md-12'),
            ),
            Row(
                Column(Field('state'), css_class='form-group myinput col-md-6'),
                Column(Field('city'), css_class='form-group myinput col-md-6'),
            ),
            Row(
                
            Column(Field('pincode'), css_class='form-group myinput col-md-6'),
            Column(Field('status'), css_class='form-group myinput col-md-6')
            ),
            
            Row(
                Column(Field('remark'), css_class='form-group myinput col-md-12'),
            ),
            
        )

class ContactForm(forms.ModelForm):
    site = forms.ModelChoiceField(queryset=Site.objects.all(), empty_label="Select Site")

    class Meta:
        model = Contacts
        fields = [
            'site', 'first_name', 'last_name', 'gender', 'address', 'state', 'city', 'pincode',
            'dob', 'event_date', 'event_date_remark', 'contact1', 'contact2', 'contact3',
            'email', 'designation', 'department'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'event_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'site',  # Initially visible
            Div(id='site-details'),  # Dynamic site info
            Div(
                Row(
                    Column(Div('first_name', css_class='input-group mb-3', prepend='<i class="fas fa-user"></i>'), css_class='form-group col-md-6 mb-0'),
                    Column(Div('last_name', css_class='input-group mb-3', prepend='<i class="fas fa-user"></i>'), css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column(Div('gender', css_class='input-group mb-3', prepend='<i class="fas fa-venus-mars"></i>'), css_class='form-group col-md-4 mb-0'),
                    Column(Div('email', css_class='input-group mb-3', prepend='<i class="fas fa-envelope"></i>'), css_class='form-group col-md-8 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column(Div('contact1', css_class='input-group mb-3', prepend='<i class="fas fa-phone"></i>'), css_class='form-group col-md-4 mb-0'),
                    Column(Div('contact2', css_class='input-group mb-3', prepend='<i class="fas fa-phone-alt"></i>'), css_class='form-group col-md-4 mb-0'),
                    Column(Div('contact3', css_class='input-group mb-3', prepend='<i class="fas fa-phone-alt"></i>'), css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column(Div('address', css_class='input-group mb-3', prepend='<i class="fas fa-map-marker-alt"></i>'), css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column(Div('city', css_class='input-group mb-3', prepend='<i class="fas fa-city"></i>'), css_class='form-group col-md-4 mb-0'),
                    Column(Div('state', css_class='input-group mb-3', prepend='<i class="fas fa-flag"></i>'), css_class='form-group col-md-4 mb-0'),
                    Column(Div('pincode', css_class='input-group mb-3', prepend='<i class="fas fa-mail-bulk"></i>'), css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column(Div('dob', css_class='input-group mb-3', prepend='<i class="fas fa-birthday-cake"></i>'), css_class='form-group col-md-6 mb-0'),
                    Column(Div('event_date', css_class='input-group mb-3', prepend='<i class="fas fa-calendar-alt"></i>'), css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column(Div('event_date_remark', css_class='input-group mb-3', prepend='<i class="fas fa-comment"></i>'), css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column(Div('designation', css_class='input-group mb-3', prepend='<i class="fas fa-briefcase"></i>'), css_class='form-group col-md-6 mb-0'),
                    Column(Div('department', css_class='input-group mb-3', prepend='<i class="fas fa-building"></i>'), css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                css_id='form-rest'
            ),
            Submit('submit', 'Save', css_class='btn btn-primary btn-sm')
        )     
# Regex validator for a 10-digit mobile number
mobile_validator = RegexValidator(
    regex=r'^\d{10}$',
    message="Enter a valid 10-digit mobile number."
)

# Regex validator for a 12-digit Aadhaar number
aadhaar_validator = RegexValidator(
    regex=r'^\d{12}$',
    message="Enter a valid 12-digit Aadhaar number."
)
  
class EmployeeForm(forms.ModelForm):
    
    # Define Regex Validators
    aadhaar_validator = RegexValidator(
        regex=r'^\d{12}$',
        message="Aadhaar number must be exactly 12 digits."
    )
    pan_validator = RegexValidator(
        regex=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$',
        message="PAN card number must be in the format ABCDE1234F."
    )
    contact_validator = RegexValidator(
        regex=r'^\d{10}$',
        message="Contact number must be exactly 10 digits."
    )
    pincode_validator = RegexValidator(
        regex=r'^\d{6}$',
        message="Pincode must be a 6-digit number."
    )
    
    # Override fields with custom validators and widgets
    contact_no = forms.CharField(
        max_length=10,
        validators=[contact_validator],
        widget=forms.TextInput(attrs={'placeholder': '10-digit mobile number'}),
        label='Contact Number'
    )
    
    emergency_contact = forms.CharField(
        max_length=10,
        required=False,
        validators=[contact_validator],
        widget=forms.TextInput(attrs={'placeholder': '10-digit mobile number'}),
        label='Emergency Contact'
    )
    
    aadhaar_no = forms.CharField(
        max_length=12,
        validators=[aadhaar_validator],
        widget=forms.TextInput(attrs={'placeholder': '12-digit Aadhaar number'}),
        label='Aadhaar Number'
    )
    
    pan_card = forms.CharField(
        max_length=10,
        required=False,
        validators=[pan_validator],
        widget=forms.TextInput(attrs={'placeholder': '10-digit PAN number'}),
        label='PAN Card'
    )

    cor_pincode = forms.CharField(
        max_length=6,
        validators=[pincode_validator],
        widget=forms.TextInput(attrs={'placeholder': '6-digit pincode'}),
        label='Pincode'
    )
    
    class Meta:
        model = Employee
        fields = [
            'first_name', 'middle_name', 'last_name', 'email', 'designation', 'gender', 'department', 'site',
            'dob', 'contact_no', 'photo', 'joining_date', 'aadhaar_no', 'pan_card',
            'other_id_proof_type', 'other_id_proof_no', 'emergency_contact',
            'bank_name', 'account_no', 'ifsc_code', 'upi_id', 'status',
            # New ones
            'father_name', 'mother_name', 'marital_status', 'blood_group',
            'per_address', 'per_city', 'per_state', 'per_pincode',
            'cor_address', 'cor_city', 'cor_state', 'cor_pincode',
            'nationality', 'uan_no', 'pf_esic_no', 'passport_no',
            'emergency_person_name', 'emergency_relation', 'emergency_alternative_no',
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
            'designation':  Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
            'department':   Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
            'site':         Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
            'cor_state':        Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
            'cor_city':         Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
            'per_state':        Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
            'per_city':         Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
            'photo':        forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status':       Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form'
        # self.helper.label_class = 'col-sm-3 col-md-4 col-lg-2'
        # self.helper.field_class = 'col-sm-9 col-md-8 col-lg-6'
        self.helper.form_tag = False  # We'll handle form tag in template
        self.helper.label_class = "font-weight-bold"
        self.helper.field_class = "mb-2"

        self.helper.layout = Layout(

            HTML("<h4 class='mt-3 mb-2'>👤 Basic Information</h4><hr>"),
            Row(
                Column(
                    Row(
                        Column(Field('first_name'), css_class="col-md-4"),
                        Column(Field('middle_name'), css_class="col-md-4"),
                        Column(Field('last_name'), css_class="col-md-4"),
                    ),
                    Row(
                        Column(Field('father_name'), css_class="col-md-4"),
                        Column(Field('mother_name'), css_class="col-md-4"),
                        Column(Field('dob'), css_class="col-md-4"),
                    ),
                    Row(
                        
                        Column(Field('gender'), css_class="col-md-4"),
                        Column(Field('marital_status'), css_class="col-md-4"),
                        Column(Field('blood_group'), css_class="col-md-4"),
                    ),
                    HTML("<h4 class='mt-3 mb-2'>📞 Contact Details</h4><hr>"),
                    Row(
                        Column(Field('email'), css_class="col-md-4"),
                        Column(Field('contact_no'), css_class="col-md-4"),
                        
                    ),
                    css_class="col-md-9"
                ),
                Column(
                    HTML(f"""
                    <div class="text-center">
                        <label class="font-weight-bold small">Photo</label>
                        <div class="photo-preview-container border rounded p-2">
                            <img id="photo-preview" src="{static("img/nopic.jpg")}" 
                                class="img-fluid" 
                                style="max-height: 200px; width: auto;">
                        </div>
                    </div>
                    """),
                    Row(Column(Field('photo'), css_class="col-md-12")),
                    css_class="col-md-3 d-flex flex-column align-items-center"
                ),
            ),
            Row(
                
                Column(
                    HTML("<h4 class='mt-3 mb-2'>🏠 Correspondence Address</h4><hr>"),            
                    Row(Column(Field('cor_address'), css_class="col-md-12")),
                    Row(
                        Column(Field('cor_state'), css_class="col-md-4"),
                        Column(Field('cor_city'), css_class="col-md-4"),
                        Column(Field('cor_pincode'), css_class="col-md-4"),
                    ),
                    css_class="col-md-6"
                ),

                Column(
                    HTML("""<div class="d-flex align-items-center mt-3 mb-2">
                        <h4 class="mb-0 mr-3">🏡 Permanent Address</h4>
                        <div class="form-check">
                            <input type="checkbox" id="same_address" class="form-check-input">
                            <label for="same_address" class="form-check-label">Same as correspondence</label>
                        </div>
                        </div><hr>
                        """),

                    Row(Column(Field('per_address'), css_class="col-md-12")),
                    Row(
                        Column(Field('per_state'), css_class="col-md-4"),
                        Column(Field('per_city'), css_class="col-md-4"),
                        Column(Field('per_pincode'), css_class="col-md-4"),
                    ),
                    css_class="col-md-6"
                ),
            ),


            HTML("<h4 class='mt-3 mb-2'>🆔 Identity Proofs</h4><hr>"),
            Row(
                Column(Field('nationality'), css_class="col-md-3"),
                Column(Field('aadhaar_no'), css_class="col-md-3"),
                Column(Field('pan_card'), css_class="col-md-3"),
                Column(Field('passport_no'), css_class="col-md-3")
            ),
            Row(
                Column(Field('other_id_proof_type'), css_class="col-md-3"),
                Column(Field('other_id_proof_no'), css_class="col-md-6")),

            HTML("<h4 class='mt-3 mb-2'>🏦 Bank Details</h4><hr>"),
            Row(
                
                Column(Field('ifsc_code'), css_class="col-md-2"),
                Column(Field('bank_name'), css_class="col-md-4"),                
                HTML("""<div class="form-group myinput col-md-6">
                    <div id="div_id_bank_name" class="form-group"> <label for="id_bank_name" class="">Branch Name & Address</label> 
                        <div class="form-control-static">
                            <input type="text" name="id_branch_details" maxlength="100"  class="textinput form-control" id="id_branch_details" disabled>
                        </div> 
                    </div> 
                </div>
                <p id="ifsc_error_message" class="text-danger font-medium mt-2"></p>"""),
            ),
            Row(
                Column(Field('account_no'), css_class="col-md-4"),
                Column(Field('upi_id'), css_class="col-md-4"),
            ),
            HTML("<h4 class='mt-3 mb-2'>🧾 Statutory Details</h4>"),
            Row(
                Column(Field('uan_no'), css_class="col-md-6"),
                Column(Field('pf_esic_no'), css_class="col-md-6"),
            ),

            HTML("<h4 class='mt-3 mb-2'>🚨 Emergency Contact Person</h4><hr>"),
            Row(
                
                Column(Field('emergency_contact'), css_class="col-md-3"),
                Column(Field('emergency_person_name'), css_class="col-md-3"),
                Column(Field('emergency_relation'), css_class="col-md-3"),
                Column(Field('emergency_alternative_no'), css_class="col-md-3"),
            ),
            
            HTML("<h4 class='mt-3 mb-2'>💼 Job Information</h4><hr>"),
            Row(
                Column(Field('designation'), css_class="col-md-4"),
                Column(Field('department'), css_class="col-md-4"),
                Column(Field('site'), css_class="col-md-4"),
            ),
            Row(
                Column(Field('joining_date'), css_class="col-md-4"),
                Column(Field('status'), css_class="col-md-4"),
            )
        )

class EmployeeEducationForm(forms.ModelForm):
    class Meta:
        model = EmployeeEducation
        fields = ['degree', 'institution', 'passing_year', 'percentage']
        widgets = {
            'passing_year': forms.NumberInput(attrs={'placeholder': 'e.g., 2020'}),
            'percentage': forms.NumberInput(attrs={'placeholder': 'e.g., 85.50'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(Field('degree'), css_class='col-md-6'),
                Column(Field('institution'), css_class='col-md-6'),
            ),
            Row(
                Column(Field('passing_year'), css_class='col-md-6'),
                Column(Field('percentage'), css_class='col-md-6'),
            ),
        )

class EmployeeExperienceForm(forms.ModelForm):
    class Meta:
        model = EmployeeExperience
        fields = ['company_name', 'job_title', 'start_date', 'end_date', 'responsibilities', 'gross_salary', 'reason_for_leaving']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'responsibilities': forms.Textarea(attrs={'rows': 3}),
            'reason_for_leaving': forms.Textarea(attrs={'rows': 3}),
            'gross_salary': forms.NumberInput(attrs={'placeholder': 'e.g., 50000.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(Field('company_name'), css_class='col-md-12'),
            ),
            Row(                
                Column(Field('job_title'), css_class='col-md-6'),                
                Column(Field('gross_salary'), css_class='col-md-6'),
            ),
            Row(
                Column(Field('start_date'), css_class='col-md-6'),
                Column(Field('end_date'), css_class='col-md-6'),
            ),
            Field('responsibilities'),
            Row(
                Column(Field('reason_for_leaving'), css_class='col-md-12'),
            ),
        )

class EmployeeFamilyForm(forms.ModelForm):
    
    
    contact_no = forms.CharField(
        max_length=10,
        required=False,
        validators=[mobile_validator],
        widget=forms.TextInput(attrs={'placeholder': '10-digit mobile number'}),
        label='Contact Number'
    )
    
    aadhaar_no = forms.CharField(
        max_length=12,
        validators=[aadhaar_validator],
        widget=forms.TextInput(attrs={'placeholder': '12-digit Aadhaar number'}),
        label='Aadhaar Number'
    )
    class Meta:
        model = EmployeeFamily
        fields = ['name', 'relationship', 'dob', 'occupation', 'aadhaar_no', 'contact_no', 'address']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'relationship': Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
            'aadhaar_no': forms.TextInput(attrs={'placeholder': '12-digit Aadhaar number'}),
            'contact_no': forms.TextInput(attrs={'placeholder': '10-digit mobile number'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(Field('name'), css_class='col-md-12'),
                
            ),
            Field('relationship'),
            Row(
                Column(Field('dob'), css_class='col-md-6'),
                Column(Field('occupation'), css_class='col-md-6'),
            ),
            Row(
                Column(Field('aadhaar_no'), css_class='col-md-6'),
                Column(Field('contact_no'), css_class='col-md-6'),
            ),
            Field('address'),
        )

class EmployeeUploadForm(forms.ModelForm):
    file = forms.FileField(required=False)  # For file upload
    class Meta:
        model = EmployeeUpload
        fields = ['document_type', 'file', 'description', 'status']
        widgets = {
            'document_type': Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
            'status': Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # We'll handle form tag in template
        self.helper.layout = Layout(
            Row(
                Column(Field('document_type'), css_class='form-group myinput col-md-2 mb-0'),
                Column(Field('file'), css_class='form-group myinput col-md-4 mb-0'),
                Column(Field('description'), css_class='form-group myinput col-md-4 mb-0'),
                Column(Field('status'), css_class='form-group myinput col-md-2 mb-0')
            ),
        )

class EmployeeUserForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=Select2Widget,
        label="Select Employee"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(Field('employee'), css_class='form-group myinput col-md-12'),
            ),
        )

    def clean_employee(self):
        employee = self.cleaned_data['employee']
        if User.objects.filter(username=employee.emp_code).exists():
            raise forms.ValidationError("A user with this employee code already exists.")
        return employee

class EmployeeSalaryMasterForm(forms.ModelForm):
    class Meta:
        model = EmployeeSalaryMaster
        fields = ['salary_amount', 'effective_from', 'status', 'remarks']
        widgets = {
            'effective_from': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(Field('salary_amount'), css_class='col-md-6'),
                Column(Field('effective_from'), css_class='col-md-6'),
            ),
            Field('status'),
            Field('remarks'),
        )

class EmployeeAdjustmentForm(forms.ModelForm):
    class Meta:
        model = EmployeeAdjustment
        fields = ['adjustment_type', 'amount', 'date', 'remarks', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'adjustment_type': forms.Select(),
            'status': forms.Select(),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(Field('adjustment_type'), css_class='col-md-4'),
                Column(Field('amount'), css_class='col-md-4'),
                Column(Field('date'), css_class='col-md-4'),
            ),
            Field('remarks'),
            Field('status'),
        )

class SalaryPreparationForm(forms.Form):
    leave_days = forms.IntegerField(initial=2, validators=[MinValueValidator(0)])
    remarks = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('leave_days'),
            Field('remarks'),
        )

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Employee Code",
        widget=forms.TextInput(attrs={'placeholder': 'Enter Employee Code', 'class': 'form-control'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(Field('username'), css_class='form-group col-md-12'),
            ),
            Row(
                Column(Field('password'), css_class='form-group col-md-12'),
            ),
        )

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'Enter Email', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(Field('email'), css_class='form-group col-md-12'),
            ),
        )