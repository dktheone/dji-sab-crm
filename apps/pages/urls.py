from django.urls import path
# from apps.emp import views as emp_views
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    # path('', emp_views.dashboard, name='dashboard'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
]
