from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'date_of_birth']
    search_fields = ['user__first_name', 'user__last_name']
