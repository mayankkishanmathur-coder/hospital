from django import forms
from .models import Appointment
from datetime import date, timedelta


class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'reason']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show all doctors in the dropdown
        from doctors.models import Doctor
        self.fields['doctor'].queryset = Doctor.objects.all()
    
    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        if appointment_date < date.today():
            raise forms.ValidationError("Appointment date cannot be in the past")
        return appointment_date


class AppointmentApprovalForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class AppointmentRejectionForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['rejection_reason']
        widgets = {
            'rejection_reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
