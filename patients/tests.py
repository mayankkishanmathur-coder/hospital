from django.test import TestCase
from django.contrib.auth.models import User
from .models import Patient
from datetime import date


class PatientModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testpatient',
            email='patient@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.patient = Patient.objects.create(
            user=self.user,
            phone='9876543210',
            address='123 Main St',
            date_of_birth=date(1990, 5, 15)
        )
    
    def test_patient_creation(self):
        self.assertEqual(self.patient.user.username, 'testpatient')
        self.assertEqual(self.patient.phone, '9876543210')
    
    def test_patient_string_representation(self):
        expected_string = f"Patient: {self.user.first_name} {self.user.last_name}"
        self.assertEqual(str(self.patient), expected_string)


class PatientViewTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testpatient',
            password='testpass123'
        )
        Patient.objects.create(
            user=self.user,
            phone='9876543210',
            address='Test Address',
            date_of_birth=date(1990, 5, 15)
        )
    
    def test_patient_login_page(self):
        response = self.client.get('/patients/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'patients/login.html')
    
    def test_patient_register_page(self):
        response = self.client.get('/patients/register/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'patients/register.html')
