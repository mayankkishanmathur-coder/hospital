from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

# Department/Clinic
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    location = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


# Doctor Specialization
class DoctorSpecialization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='specializations')
    
    def __str__(self):
        return self.name


# Doctor Profile
class Doctor(models.Model):
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('on_break', 'On Break'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.ForeignKey(DoctorSpecialization, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors')
    phone = models.CharField(max_length=15)
    license_number = models.CharField(max_length=50, unique=True)
    experience_years = models.IntegerField()
    clinic_address = models.TextField()
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='available')
    consultation_fee = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.FloatField(default=0.0)  # Average rating (0-5)
    total_ratings = models.IntegerField(default=0)  # Count of ratings
    qualifications = models.TextField(blank=True, null=True)  # Education/certifications
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='doctor_profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"
    
    def update_rating(self):
        """Calculate average rating from AppointmentRating"""
        from appointments.models import AppointmentRating
        ratings = AppointmentRating.objects.filter(doctor=self)
        if ratings.exists():
            avg_rating = ratings.aggregate(models.Avg('rating'))['rating__avg']
            self.rating = avg_rating or 0.0
            self.total_ratings = ratings.count()
            self.save()


# Doctor Availability Schedule
class DoctorAvailability(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration = models.IntegerField(default=30)  # Duration in minutes
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['doctor', 'day_of_week']
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.doctor} - {self.day_of_week}"
