



# apps/leads/apps.py
from django.apps import AppConfig

class LeadsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.leads'  # Must match the INSTALLED_APPS entry exactly
    verbose_name = 'Leads Management'  # Human-readable name for admin