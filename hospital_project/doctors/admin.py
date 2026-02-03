from django.contrib import admin
from .models import Doctor, DoctorSpecialization

@admin.register(DoctorSpecialization)
class DoctorSpecializationAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'license_number', 'availability_status']
    search_fields = ['user__first_name', 'user__last_name', 'specialization__name']
    list_filter = ['specialization', 'availability_status']
