from django.contrib.auth import get_user_model
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()
admin_user = User.objects.get(username='admin')
admin_user.set_password('admin123')  # Change this to your preferred password
admin_user.save()
print("Admin password set successfully!")
