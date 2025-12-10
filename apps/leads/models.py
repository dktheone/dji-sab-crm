from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from apps.emp.models import Employee, Site  # Integrate with existing Employee and Site
from datetime import date

User = get_user_model()

class LeadStatus(models.TextChoices):
    NEW = 'New', 'New'
    IN_PROGRESS = 'In Progress', 'In Progress'
    QUOTED = 'Quoted', 'Quoted'
    CONVERTED = 'Converted', 'Converted'  # Links to active Site
    NOT_INTERESTED = 'Not Interested', 'Not Interested'
    CLOSED = 'Closed', 'Closed'

class CustomerType(models.TextChoices):
    HOSPITAL = 'Hospital', 'Hospital'
    INSTITUTE = 'Institute', 'Institute'
    EVENT = 'Event', 'Event'
    HOSTEL = 'Hostel', 'Hostel'

class RequirementType(models.TextChoices):
    DIET_SERVICE = 'Diet Service', 'Diet Service'
    CAFETERIA = 'Cafeteria', 'Cafeteria'
    EVENT_CATERING = 'Event Catering', 'Event Catering'
    OTHERS = 'Others', 'Others'

class FeedbackType(models.TextChoices):
    POSITIVE = 'Positive', 'Positive'
    NEGATIVE = 'Negative', 'Negative'
    NEUTRAL = 'Neutral', 'Neutral'

class Lead(models.Model):
    lead_id = models.AutoField(primary_key=True)  # S.No.
    entry_date = models.DateField(default=date.today, verbose_name="Entry Date")
    customer_type = models.CharField(max_length=20, choices=CustomerType.choices, default=CustomerType.HOSPITAL)
    client_name = models.CharField(max_length=200, verbose_name="Hospital / Customer Name")
    total_beds = models.PositiveIntegerField(blank=True, null=True, verbose_name="Total Beds")
    current_occupancy = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True, null=True, verbose_name="Current Occupancy (%)"
    )
    contact_person = models.CharField(max_length=100, verbose_name="Contact Person Name")
    designation = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True, verbose_name="Email Address")
    address = models.TextField(verbose_name="Complete Address / Location")
    existing_vendor = models.CharField(max_length=200, blank=True, null=True, verbose_name="Existing Vendor / Caterer")
    has_service_requirement = models.BooleanField(default=False, verbose_name="Has Service Requirement?")
    service_requirement = models.CharField(max_length=20, choices=RequirementType.choices, blank=True, null=True, verbose_name="Service Requirement")
    lead_status = models.CharField(max_length=20, choices=LeadStatus.choices, default=LeadStatus.NEW)
    next_follow_up = models.DateField(blank=True, null=True, verbose_name="Next Follow-up Date")
    remarks = models.TextField(blank=True, null=True, verbose_name="Remarks / Notes")
    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leads_created', verbose_name="Sales Employee")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    converted_site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True, related_name='lead_source')  # Link to active Site on conversion

    class Meta:
        db_table = 'leads'
        ordering = ['-entry_date']
        verbose_name = "Potential Site Lead"
        verbose_name_plural = "Potential Site Leads"

    def __str__(self):
        return f"{self.lead_id} - {self.client_name} ({self.lead_status})"

    def save(self, *args, **kwargs):
        if self.lead_status == LeadStatus.CONVERTED and not self.converted_site:
            raise ValueError("Converted leads must link to an active Site.")
        super().save(*args, **kwargs)

class FollowUp(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='follow_ups')
    follow_up_date = models.DateField(verbose_name="Last Follow-Up Date")
    feedback = models.CharField(max_length=20, choices=FeedbackType.choices, verbose_name="Feedback")
    quotation_sent = models.BooleanField(default=False, verbose_name="Quotation Sent")
    quotation_date = models.DateField(blank=True, null=True, verbose_name="Quotation Date")
    closing_date = models.DateField(blank=True, null=True, verbose_name="Closing Date")
    next_follow_up_date = models.DateField(blank=True, null=True, verbose_name="Next Follow-up Date")
    remarks = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='follow_ups_created', verbose_name="Sales Employee")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lead_follow_ups'
        ordering = ['-follow_up_date']
        verbose_name = "Lead Follow-up"
        verbose_name_plural = "Lead Follow-ups"

    def __str__(self):
        return f"Follow-up for {self.lead.lead_id} on {self.follow_up_date} by {self.created_by}"

    def save(self, *args, **kwargs):
        # BUG FIX #1: Auto-fill quotation date if quotation sent
        if self.quotation_sent and not self.quotation_date:
            self.quotation_date = date.today()
        
        # BUG FIX #2: Update lead status to QUOTED when quotation is sent
        if self.quotation_sent and self.lead.lead_status == LeadStatus.IN_PROGRESS:
            self.lead.lead_status = LeadStatus.QUOTED
            self.lead.save(update_fields=['lead_status'])
        
        # BUG FIX #1: Only close lead if not already in terminal state and closing_date provided
        if self.closing_date and self.lead.lead_status not in [LeadStatus.CONVERTED, LeadStatus.CLOSED]:
            self.lead.lead_status = LeadStatus.CLOSED
            self.lead.save(update_fields=['lead_status'])
        
        super().save(*args, **kwargs)
        
        # BUG FIX #3: Auto-update lead's next follow-up date
        if self.next_follow_up_date:
            self.lead.next_follow_up = self.next_follow_up_date
            self.lead.save(update_fields=['next_follow_up'])
        
        
        
        
# ... (existing imports and models remain the same)

class LeadConversionLog(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='conversion_logs')
    site = models.ForeignKey('emp.Site', on_delete=models.CASCADE, related_name='lead_conversions')  # FK to emp.Site
    converted_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='conversions_made', verbose_name="Converted By")
    conversion_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True, verbose_name="Conversion Notes")

    class Meta:
        db_table = 'lead_conversion_logs'
        ordering = ['-conversion_date']
        verbose_name = "Lead Conversion Log"
        verbose_name_plural = "Lead Conversion Logs"

    def __str__(self):
        return f"Conversion of {self.lead.lead_id} to Site {self.site.site_name} on {self.conversion_date.date()}"


class LeadContact(models.Model):
    """Multiple contacts for each lead"""
    
    class ContactStatus(models.TextChoices):
        ACTIVE = 'Active', 'Active'
        INACTIVE = 'Inactive', 'Inactive'
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='contacts', verbose_name="Lead")
    name = models.CharField(max_length=100, verbose_name="Contact Name")
    designation = models.CharField(max_length=100, verbose_name="Designation")
    mobile1 = models.CharField(max_length=15, verbose_name="Mobile 1")
    mobile2 = models.CharField(max_length=15, blank=True, null=True, verbose_name="Mobile 2")
    landline = models.CharField(max_length=20, blank=True, null=True, verbose_name="Landline")
    email = models.EmailField(blank=True, null=True, verbose_name="Email Address")
    remarks = models.TextField(blank=True, null=True, verbose_name="Remarks")
    status = models.CharField(
        max_length=10,
        choices=ContactStatus.choices,
        default=ContactStatus.ACTIVE,
        verbose_name="Status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lead_contacts'
        ordering = ['-created_at']
        verbose_name = "Lead Contact"
        verbose_name_plural = "Lead Contacts"
    
    def __str__(self):
        return f"{self.name} - {self.lead.client_name}"