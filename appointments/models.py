from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from patients.models import Patient
from doctors.models import Doctor
from datetime import timedelta


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # New fields
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    payment_id = models.CharField(max_length=100, blank=True, null=True)  # Stripe/PayPal ID
    is_video_consultation = models.BooleanField(default=False)
    video_link = models.URLField(blank=True, null=True)  # Zoom/Jitsi link
    reminder_sent = models.BooleanField(default=False)
    follow_up_appointment = models.OneToOneField('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='original_appointment')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
    
    def __str__(self):
        return f"Appointment: {self.patient.user.first_name} with {self.doctor} on {self.appointment_date}"
    
    def is_reminder_due(self):
        """Check if appointment reminder should be sent (24 hours before)"""
        if self.reminder_sent:
            return False
        appointment_datetime = timezone.make_aware(
            timezone.datetime.combine(self.appointment_date, self.appointment_time)
        )
        return timezone.now() >= appointment_datetime - timedelta(hours=24)
    
    def mark_reminder_sent(self):
        """Mark reminder as sent"""
        self.reminder_sent = True
        self.save()


class DoctorNote(models.Model):
    """Doctor's notes/prescriptions for completed appointments"""
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='doctor_note')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='notes')
    prescription = models.TextField()  # Medications prescribed
    clinical_notes = models.TextField()  # Doctor's observations
    follow_up_required = models.BooleanField(default=False)
    follow_up_days = models.IntegerField(default=7)  # Suggest follow-up after N days
    attachments = models.FileField(upload_to='prescriptions/', blank=True, null=True)  # PDF, reports, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notes for {self.appointment}"
    
    def get_follow_up_date(self):
        """Calculate suggested follow-up appointment date"""
        if self.follow_up_required:
            return self.appointment.appointment_date + timedelta(days=self.follow_up_days)
        return None


class AppointmentRating(models.Model):
    """Patient ratings and reviews for appointments"""
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='rating')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='ratings_given')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='ratings_received')
    rating = models.IntegerField(choices=[(i, f"{i} Star") for i in range(1, 6)])  # 1-5 stars
    review_text = models.TextField(blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['appointment', 'patient']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.patient.user.first_name} rated {self.doctor} - {self.rating} stars"


class WaitingList(models.Model):
    """Queue for appointments when doctor is fully booked"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='waiting_list_entries')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='waiting_list')
    preferred_date_from = models.DateField()
    preferred_date_to = models.DateField()
    reason = models.TextField()
    position_in_queue = models.IntegerField()
    is_notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('waiting', 'Waiting'), ('offered', 'Offered'), ('booked', 'Booked'), ('cancelled', 'Cancelled')],
        default='waiting'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['patient', 'doctor']
        ordering = ['position_in_queue']
    
    def __str__(self):
        return f"{self.patient.user.first_name} waiting for {self.doctor}"
