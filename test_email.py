"""
Test script to verify email configuration
Run this script directly: python test_email.py
"""
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 60)
print("Testing Email Configuration")
print("=" * 60)
print(f"Email Backend: {settings.EMAIL_BACKEND}")
print(f"Email Host: {settings.EMAIL_HOST}")
print(f"Email Port: {settings.EMAIL_PORT}")
print(f"Email Use SSL: {settings.EMAIL_USE_SSL}")
print(f"Email User: {settings.EMAIL_HOST_USER}")
print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
print("=" * 60)

# Send test email
try:
    result = send_mail(
        subject='SAB CRM - Test Email',
        message='This is a test email from SAB CRM to verify SMTP configuration.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['info@sabhospitality.com'],  # Send to same email for testing
        fail_silently=False,
    )
    print(f"[OK] Email sent successfully! Result: {result}")
    print("Check the inbox of info@sabhospitality.com")
except Exception as e:
    print(f"[ERROR] Email sending failed: {str(e)}")
    print(f"Error type: {type(e).__name__}")

print("=" * 60)
