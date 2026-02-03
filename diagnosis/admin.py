from django.contrib.admin import site, ModelAdmin, register
from .models import Symptom, DiagnosisRecord


@register(Symptom)
class SymptomAdmin(ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@register(DiagnosisRecord)
class DiagnosisRecordAdmin(ModelAdmin):
    list_display = ('patient', 'predicted_condition', 'predicted_specialization', 'confidence_score', 'created_at')
    list_filter = ('predicted_specialization', 'created_at', 'confidence_score')
    search_fields = ('patient__user__username', 'predicted_condition')
    readonly_fields = ('created_at', 'confidence_score')
    filter_horizontal = ('symptoms',)
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient',)
        }),
        ('Diagnosis Results', {
            'fields': ('symptoms', 'predicted_condition', 'predicted_specialization', 'confidence_score')
        }),
        ('Booking', {
            'fields': ('booked_doctor',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
