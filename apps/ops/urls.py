from django.urls import path
from .views import BackupListView

app_name = 'ops'

urlpatterns = [
    path('backups/', BackupListView.as_view(), name='backup_list'),
]
