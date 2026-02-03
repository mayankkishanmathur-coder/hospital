from django.db import models
from django.utils import timezone
from patients.models import Patient
from appointments.models import Appointment


class Bill(models.Model):
    """Store billing information for appointments and services"""
    BILL_TYPE_CHOICES = [
        ('consultation', 'Consultation Fee'),
        ('diagnosis', 'Diagnosis Test'),
        ('procedure', 'Medical Procedure'),
        ('follow_up', 'Follow-up Visit'),
        ('medication', 'Medication'),
        ('service', 'Service Charge'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bills')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='bills')
    
    bill_type = models.CharField(max_length=20, choices=BILL_TYPE_CHOICES, default='consultation')
    description = models.TextField(blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    
    bill_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-bill_date']
        verbose_name = 'Bill'
        verbose_name_plural = 'Bills'
    
    def __str__(self):
        return f"Bill #{self.id} - {self.patient.user.get_full_name()} - ${self.amount}"
    
    @property
    def total_amount(self):
        """Calculate total with tax and discount"""
        return self.amount + self.tax - self.discount
    
    @property
    def remaining_amount(self):
        """Calculate remaining amount to be paid"""
        return self.total_amount - self.paid_amount
    
    @property
    def is_overdue(self):
        """Check if bill is overdue"""
        if self.payment_status == 'paid':
            return False
        if self.due_date and self.due_date < timezone.now().date():
            return True
        return False

