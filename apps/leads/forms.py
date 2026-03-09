from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, HTML, Submit
from django_select2.forms import Select2Widget
from .models import Lead, FollowUp, LeadStatus, RequirementType, CustomerType, FeedbackType

from apps.emp.models import Site  # Import for form


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            'customer_type', 'client_name', 'total_beds', 'current_occupancy',
            'address', 'existing_vendor', 
            'has_service_requirement', 'service_requirement',
            'lead_status', 'next_follow_up', 'remarks'
        ]
        widgets = {
            'customer_type': Select2Widget(attrs={'class': 'form-control custom_select'}),
            'service_requirement': Select2Widget(attrs={'class': 'form-control custom_select'}),
            'lead_status': Select2Widget(attrs={'class': 'form-control custom_select'}),
            'next_follow_up': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'font-weight-bold'
        self.helper.layout = Layout(
            HTML("<h4 class='mt-3 mb-2'>🏥 Lead Details</h4><hr>"),
            Row(
                Column(Field('customer_type'), css_class='col-md-4'),
                Column(Field('client_name'), css_class='col-md-8'),
            ),
            Row(
                Column(Field('total_beds'), css_class='col-md-4'),
                Column(Field('current_occupancy'), css_class='col-md-4'),
            ),
            HTML("<h4 class='mt-3 mb-2'>📋 Service Requirements</h4><hr>"),
            Row(
                Column(Field('has_service_requirement'), css_class='col-md-6'),
                Column(Field('service_requirement', css_id='id_service_requirement_field'), css_class='col-md-6'),
            ),
            Field('existing_vendor'),
            HTML("<h4 class='mt-3 mb-2'>👤 Contact Information</h4><hr>"),
            Row(
                Column(Field('contact_person'), css_class='col-md-4'),
                Column(Field('designation'), css_class='col-md-4'),
                Column(Field('mobile_no'), css_class='col-md-4'),
            ),
            Row(
                Column(Field('email'), css_class='col-md-12'),
            ),
            HTML("<h4 class='mt-3 mb-2'>📍 Address & Status</h4><hr>"),
            Field('address'),
            Row(
                Column(Field('lead_status'), css_class='col-md-4'),
                Column(Field('next_follow_up'), css_class='col-md-4'),
            ),
            Field('remarks'),
            HTML("""
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    const checkbox = document.getElementById('id_has_service_requirement');
                    const serviceField = document.getElementById('id_service_requirement_field').closest('.col-md-6');
                    
                    function toggleServiceField() {
                        if (checkbox.checked) {
                            serviceField.style.display = 'block';
                        } else {
                            serviceField.style.display = 'none';
                            document.getElementById('id_service_requirement').value = '';
                        }
                    }
                    
                    checkbox.addEventListener('change', toggleServiceField);
                    toggleServiceField(); // Initial state
                });
            </script>
            """),
        )

class FollowUpForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = ['follow_up_date', 'feedback', 'quotation_sent', 'quotation_date', 'closing_date', 'next_follow_up_date', 'remarks']
        widgets = {
            'follow_up_date': forms.DateInput(attrs={'type': 'date'}),
            'feedback': Select2Widget(attrs={'class': 'form-control custom_select'}),
            'quotation_date': forms.DateInput(attrs={'type': 'date'}),
            'closing_date': forms.DateInput(attrs={'type': 'date'}),
            'next_follow_up_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'font-weight-bold'
        self.helper.layout = Layout(
            Row(
                Column(Field('follow_up_date'), css_class='col-md-4'),
                Column(Field('feedback'), css_class='col-md-4'),
                Column(Field('next_follow_up_date'), css_class='col-md-4'),
            ),
            Row(
                Column(
                    Field('quotation_sent'), 
                    css_class='col-md-4 d-flex align-items-center mt-4'
                ),
                Column(Field('quotation_date', css_class='quotation-details'), css_class='col-md-4 quotation-details'),
                Column(Field('closing_date'), css_class='col-md-4'),
            ),
            Field('remarks'),
            HTML("""
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    const quoteCheckbox = document.getElementById('id_quotation_sent');
                    const quoteDateField = document.getElementById('div_id_quotation_date'); // Crispy forms wrap in div_id_FIELDNAME
                    
                    function toggleQuoteDate() {
                        if(quoteCheckbox && quoteDateField) {
                            if(quoteCheckbox.checked) {
                                quoteDateField.style.display = 'block';
                            } else {
                                quoteDateField.style.display = 'none';
                                document.getElementById('id_quotation_date').value = '';
                            }
                        }
                    }
                    
                    if(quoteCheckbox) {
                        quoteCheckbox.addEventListener('change', toggleQuoteDate);
                        toggleQuoteDate(); // Initial
                    }
                });
            </script>
            """)
        )




class SiteConversionForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['site_name', 'address', 'city', 'state', 'pincode', 'status', 'remark']
        widgets = {
            'status': Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
            'state': Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
            'city': Select2Widget(attrs={'class': 'form-control form-select custom_select'}),
        }

    def __init__(self, *args, lead=None, **kwargs):
        super().__init__(*args, **kwargs)
        if lead:
            # Pre-populate from Lead
            self.initial['site_name'] = lead.client_name
            self.initial['address'] = lead.address
            # Map other fields as needed (e.g., parse city/state from address if available)
            self.initial['remark'] = f"Converted from Lead #{lead.lead_id}: {lead.remarks[:100]}..." if lead.remarks else ""
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'font-weight-bold'
        self.helper.layout = Layout(
            HTML("<h4 class='mt-3 mb-2'>🔄 Conversion Details</h4><hr>"),
            Row(
                Column(Field('site_name'), css_class='col-md-12'),
                Column(Field('status'), css_class='col-md-6'),
            ),
            Row(
                Column(Field('address'), css_class='col-md-12'),
            ),
            Row(
                Column(Field('state'), css_class='col-md-4'),
                Column(Field('city'), css_class='col-md-4'),
                Column(Field('pincode'), css_class='col-md-4'),
            ),
            Field('remark'),
            HTML("<div class='mt-3'><small class='text-muted'>Converting Lead #{{ lead.lead_id }}: {{ lead.client_name }}</small></div>"),
        )