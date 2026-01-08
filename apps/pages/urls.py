from django.urls import path
# from apps.emp import views as emp_views
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    # path('', emp_views.dashboard, name='dashboard'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms-of-service/', views.TermsOfServiceView.as_view(), name='terms_of_service'),
]
