from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

from django.views.generic import TemplateView

def index(request):
    # Page from the theme 
    return render(request, 'pages/index.html')

class PrivacyPolicyView(TemplateView):
    template_name = 'pages/privacy_policy.html'

class TermsOfServiceView(TemplateView):
    template_name = 'pages/terms_of_service.html'
