from django.contrib import admin
from patients.models import Patient, PatientMedicalHistory
from doctors.models import Doctor, DoctorSpecialization, Department, DoctorAvailability
from appointments.models import Appointment, DoctorNote, AppointmentRating, WaitingList


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'insurance_status', 'blood_type', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'insurance_id')
    list_filter = ('insurance_status', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PatientMedicalHistory)
class PatientMedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('patient', 'diagnosis', 'created_at')
    search_fields = ('patient__user__first_name', 'diagnosis')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'phone')
    search_fields = ('name', 'location')


@admin.register(DoctorSpecialization)
class DoctorSpecializationAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    search_fields = ('name',)
    list_filter = ('department',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'rating', 'total_ratings', 'consultation_fee', 'availability_status')
    search_fields = ('user__first_name', 'user__last_name', 'license_number')
    list_filter = ('specialization', 'availability_status', 'rating')
    readonly_fields = ('rating', 'total_ratings', 'created_at', 'updated_at')


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'day_of_week', 'start_time', 'end_time', 'slot_duration', 'is_available')
    search_fields = ('doctor__user__first_name',)
    list_filter = ('day_of_week', 'is_available')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'appointment_time', 'status', 'payment_status')
    search_fields = ('patient__user__first_name', 'doctor__user__first_name')
    list_filter = ('status', 'payment_status', 'appointment_date')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DoctorNote)
class DoctorNoteAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'appointment', 'follow_up_required', 'created_at')
    search_fields = ('doctor__user__first_name', 'appointment__patient__user__first_name')
    list_filter = ('follow_up_required', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AppointmentRating)
class AppointmentRatingAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'rating', 'is_anonymous', 'created_at')
    search_fields = ('doctor__user__first_name', 'patient__user__first_name')
    list_filter = ('rating', 'is_anonymous', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WaitingList)
class WaitingListAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'position_in_queue', 'status', 'is_notified', 'created_at')
    search_fields = ('patient__user__first_name', 'doctor__user__first_name')
    list_filter = ('status', 'is_notified', 'created_at')
