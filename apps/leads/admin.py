# apps/leads/admin.py
from django.contrib import admin
from .models import Lead, FollowUp, LeadConversionLog

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['lead_id', 'client_name', 'lead_status', 'next_follow_up', 'created_by']
    list_filter = ['lead_status', 'customer_type', 'created_by']
    search_fields = ['client_name', 'contact_person']

@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ['lead', 'follow_up_date', 'feedback', 'created_by']
    list_filter = ['feedback', 'quotation_sent']

@admin.register(LeadConversionLog)
class LeadConversionLogAdmin(admin.ModelAdmin):
    list_display = ['lead', 'site', 'conversion_date', 'converted_by']
    readonly_fields = ['conversion_date']