from django.db import models


class Symptom(models.Model):
    """Store predefined symptoms for diagnosis"""
    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True)  # e.g., "respiratory", "digestive"
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='moderate')
    is_urgent = models.BooleanField(default=False)  # Flag for emergency symptoms
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"


class DiagnosisRecord(models.Model):
    """Store diagnosis results for tracking and analytics"""
    CONFIDENCE_LEVELS = [
        ('low', 'Low (< 60%)'),
        ('medium', 'Medium (60-80%)'),
        ('high', 'High (> 80%)'),
    ]
    
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='diagnosis_records')
    symptoms = models.ManyToManyField(Symptom, related_name='diagnosis_records')
    predicted_condition = models.CharField(max_length=200)
    predicted_specialization = models.ForeignKey('doctors.DoctorSpecialization', on_delete=models.SET_NULL, null=True)
    confidence_score = models.FloatField(default=0.0)
    confidence_level = models.CharField(max_length=10, choices=CONFIDENCE_LEVELS, editable=False)
    has_urgent_symptoms = models.BooleanField(default=False)  # Auto-detect from selected symptoms
    booked_doctor = models.ForeignKey('doctors.Doctor', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Auto-calculate confidence level
        if self.confidence_score < 0.6:
            self.confidence_level = 'low'
        elif self.confidence_score >= 0.8:
            self.confidence_level = 'high'
        else:
            self.confidence_level = 'medium'
        
        # First save the object so it has an ID for M2M access
        super().save(*args, **kwargs)
        
        # Then auto-detect urgent symptoms (after object is saved)
        self.has_urgent_symptoms = self.symptoms.filter(is_urgent=True).exists()
        
        # Update if urgent symptoms were detected
        if 'force_insert' not in kwargs:
            super().save(update_fields=['has_urgent_symptoms'])

    def __str__(self):
        if self.created_at:
            return f"{self.patient} - {self.predicted_condition} ({self.created_at.strftime('%Y-%m-%d')})"
        return f"{self.patient} - {self.predicted_condition}"
