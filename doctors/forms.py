from django import forms
from .models import Doctor, DoctorSpecialization
from django.contrib.auth.models import User


class DoctorRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    
    class Meta:
        model = Doctor
        fields = ['specialization', 'phone', 'license_number', 'experience_years', 'clinic_address', 'consultation_fee']
        widgets = {
            'clinic_address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match")
        
        if User.objects.filter(username=cleaned_data.get('username')).exists():
            raise forms.ValidationError("Username already exists")
        
        if Doctor.objects.filter(license_number=cleaned_data.get('license_number')).exists():
            raise forms.ValidationError("License number already registered")
        
        return cleaned_data


class DoctorLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class DoctorAvailabilityForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['availability_status']
