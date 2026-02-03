from django.test import TestCase
from django.contrib.auth.models import User
from patients.models import Patient
from doctors.models import Doctor, DoctorSpecialization
from .models import Appointment
from datetime import date, time


class AppointmentModelTest(TestCase):
    
    def setUp(self):
        # Create specialization
        self.specialization = DoctorSpecialization.objects.create(
            name='General Medicine',
            description='General health'
        )
        
        # Create patient
        patient_user = User.objects.create_user(
            username='testpatient',
            password='testpass123'
        )
        self.patient = Patient.objects.create(
            user=patient_user,
            phone='9876543210',
            address='Test Address',
            date_of_birth=date(1990, 5, 15)
        )
        
        # Create doctor
        doctor_user = User.objects.create_user(
            username='testdoctor',
            password='testpass123'
        )
        self.doctor = Doctor.objects.create(
            user=doctor_user,
            specialization=self.specialization,
            phone='1234567890',
            license_number='MD123456',
            experience_years=5,
            clinic_address='Clinic',
            consultation_fee=500.00
        )
        
        # Create appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date(2026, 2, 15),
            appointment_time=time(10, 30),
            reason='Regular checkup'
        )
    
    def test_appointment_creation(self):
        self.assertEqual(self.appointment.status, 'pending')
        self.assertEqual(self.appointment.patient, self.patient)
        self.assertEqual(self.appointment.doctor, self.doctor)
    
    def test_appointment_status_change(self):
        self.appointment.status = 'approved'
        self.appointment.save()
        self.assertEqual(self.appointment.status, 'approved')
