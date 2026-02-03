from django.apps import AppConfig

class HospitalProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hospital_project'
    
    def ready(self):
        # Import admin configuration when app is ready
        import admin_configuration
