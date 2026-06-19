from django.apps import AppConfig


class EmpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.emp"

    def ready(self):
        import apps.emp.signals
