from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    # Main views
    path('', views.vendor_list, name='vendor_list'),
    path('create/', views.vendor_create, name='vendor_create'),
    path('<int:vendor_id>/', views.vendor_detail, name='vendor_detail'),
    path('<int:vendor_id>/update/', views.vendor_update, name='vendor_update'),
    path('<int:vendor_id>/delete/', views.vendor_delete, name='vendor_delete'),
    
    # Payment information
    path('<int:vendor_id>/payment/', views.vendor_payment_create_update, name='vendor_payment'),
    
    # API endpoints for Registration IDs
    path('<int:vendor_id>/registration-ids/', views.api_vendor_registration_ids, name='api_vendor_registration_ids'),
    path('<int:vendor_id>/registration-ids/create/', views.api_vendor_registration_id_create, name='api_vendor_registration_id_create'),
    path('registration-ids/<int:reg_id>/update/', views.api_vendor_registration_id_update, name='api_vendor_registration_id_update'),
    path('registration-ids/<int:reg_id>/delete/', views.api_vendor_registration_id_delete, name='api_vendor_registration_id_delete'),
    
    # API endpoints for Documents
    path('<int:vendor_id>/documents/', views.api_vendor_documents, name='api_vendor_documents'),
    path('<int:vendor_id>/documents/upload/', views.api_vendor_document_upload, name='api_vendor_document_upload'),
    path('documents/<int:doc_id>/delete/', views.api_vendor_document_delete, name='api_vendor_document_delete'),
]
