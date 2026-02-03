from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import datetime

# Patient Profile
class Patient(models.Model):
    INSURANCE_STATUS_CHOICES = [
        ('none', 'No Insurance'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField()
    insurance_status = models.CharField(max_length=20, choices=INSURANCE_STATUS_CHOICES, default='none')
    insurance_provider = models.CharField(max_length=100, blank=True, null=True)
    insurance_id = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    blood_type = models.CharField(max_length=5, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Patient: {self.user.first_name} {self.user.last_name}"


# Patient Medical History
class PatientMedicalHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_history')
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True, related_name='medical_record')
    diagnosis = models.TextField()
    medications = models.TextField()  # Comma-separated or JSON
    allergies = models.TextField(blank=True, null=True)
    previous_conditions = models.TextField(blank=True, null=True)
    family_history = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Medical History: {self.patient.user.first_name} - {self.diagnosis[:50]}"
