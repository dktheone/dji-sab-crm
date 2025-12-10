import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from apps.leads.models import Lead

print("\n" + "="*70)
print("DIAGNOSTIC: Lead Data Check")
print("="*70 + "\n")

leads = Lead.objects.all()
print(f"Total leads in database: {leads.count()}\n")

if leads.count() == 0:
    print("No leads found in database.")
else:
    for lead in leads:
        print(f"{'='*70}")
        print(f"Lead ID: {lead.lead_id}")
        print(f"{'='*70}")
        print(f"Client Name:          {lead.client_name}")
        print(f"Customer Type:        {lead.customer_type}")
        print(f"Contact Person:       {lead.contact_person}")
        print(f"Designation:          {lead.designation}")
        print(f"Mobile:               {lead.mobile_no}")
        print(f"Email:                {lead.email or 'None'}")
        print(f"Total Beds:           {lead.total_beds or 'None'}")
        print(f"Occupancy:            {lead.current_occupancy or 'None'}")
        print(f"Address:              {(lead.address[:60] + '...') if len(lead.address) > 60 else lead.address}")
        print(f"Existing Vendor:      {lead.existing_vendor or 'None'}")
        print(f"Has Service Req:      {lead.has_service_requirement}")
        print(f"Service Requirement:  {lead.service_requirement or 'None'}")
        print(f"Lead Status:          {lead.lead_status}")
        print(f"Next Follow-up:       {lead.next_follow_up or 'None'}")
        print(f"Remarks:              {(lead.remarks[:50] + '...') if lead.remarks and len(lead.remarks) > 50 else (lead.remarks or 'None')}")
        print(f"Created By:           {lead.created_by.first_name} {lead.created_by.last_name} ({lead.created_by.emp_code})")
        print(f"Created At:           {lead.created_at}")
        print()

print("\n" + "="*70)
print("CONSISTENCY CHECK")
print("="*70 + "\n")

# Check for inconsistent data
inconsistent = Lead.objects.filter(
    has_service_requirement=False
).exclude(service_requirement__isnull=True).exclude(service_requirement='')

print(f"Leads with has_service_requirement=False but service_requirement filled: {inconsistent.count()}")
if inconsistent.exists():
    print("WARNING: Data inconsistency detected!")
    for lead in inconsistent:
        print(f"  - Lead {lead.lead_id}: {lead.client_name} has service_requirement='{lead.service_requirement}' but checkbox is False")

print("\n" + "="*70)
print("FIELD ORDER CHECK")
print("="*70 + "\n")

print("Model field order:")
for i, field in enumerate(Lead._meta.fields, 1):
    print(f"{i:2}. {field.name:25} ({field.get_internal_type()})")

print("\n" + "="*70)
