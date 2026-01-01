from django.apps import AppConfig


class HospitalHrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hospital_hr'
    
    def ready(self):
        import hospital_hr.signals
