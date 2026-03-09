# from django.urls import path
# from . import views

# app_name = 'leads'

# urlpatterns = [
#     path('', views.lead_list, name='lead_list'),
#     path('add/', views.lead_form, name='lead_form'),
#     path('edit/<int:lead_id>/', views.lead_form, name='lead_edit'),
#     path('<int:lead_id>/follow-ups/', views.lead_follow_ups, name='lead_follow_ups'),
#     path('<int:lead_id>/convert/', views.convert_to_site, name='convert_to_site'),
#     path('activity/<int:employee_id>/', views.employee_activity, name='employee_activity'),
#     path('<int:lead_id>/convert/', views.convert_to_site, name='convert_to_site'),
#     path('conversion-logs/', views.conversion_logs, name='conversion_logs'),
# ]


# apps/leads/urls.py
from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    path('', views.lead_list, name='lead_list'),
    path('form/', views.lead_form, name='lead_form_add'),  # Add new lead (no ID)
    path('form/<int:lead_id>/', views.lead_form, name='lead_form'),  # Handles add (no id) and edit (with id)
    path('<int:lead_id>/follow-ups/', views.lead_follow_ups, name='lead_follow_ups'),
    path('<int:lead_id>/convert/', views.convert_to_site, name='convert_to_site'),
    path('activity/<int:employee_id>/', views.employee_activity, name='employee_activity'),
    path('activity/', views.my_activity, name='my_activity'),  # Redirect to own activity
    path('conversion-logs/', views.conversion_logs, name='conversion_logs'),
    path('upcoming-followups/', views.upcoming_followups, name='upcoming_followups'),
    
    # Lead Contacts CRUD
    path('contacts/all/', views.all_lead_contacts, name='all_lead_contacts'),
    path('<int:lead_id>/contacts/', views.lead_contacts_list, name='lead_contacts_list'),
    path('<int:lead_id>/contacts/create/', views.lead_contact_create, name='lead_contact_create'),
    path('contacts/<int:contact_id>/update/', views.lead_contact_update, name='lead_contact_update'),
    path('contacts/<int:contact_id>/delete/', views.lead_contact_delete, name='lead_contact_delete'),
]
