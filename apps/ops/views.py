import os
import datetime
from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.conf import settings
from django.shortcuts import render

class BackupListView(UserPassesTestMixin, TemplateView):
    template_name = 'ops/backup_list.html'

    def test_func(self):
        # Only allow admin users
        return self.request.user.is_superuser or self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        backup_dir = settings.BASE_DIR / 'backups'
        backups = []
        
        if backup_dir.exists():
            for f in backup_dir.glob('*.7z'):
                try:
                    stat = f.stat()
                    backups.append({
                        'name': f.name,
                        'size': f"{stat.st_size / (1024 * 1024):.2f} MB",
                        'path': str(f),
                        'created_at': datetime.datetime.fromtimestamp(stat.st_mtime)
                    })
                except Exception:
                    pass
        
        # Sort by creation date descending
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        context['backups'] = backups
        return context
