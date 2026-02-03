from django.test import TestCase
from django.contrib.auth.models import User
from .models import Doctor, DoctorSpecialization


class DoctorModelTest(TestCase):
    
    def setUp(self):
        self.specialization = DoctorSpecialization.objects.create(
            name='Cardiology',
            description='Heart specialist'
        )
        self.user = User.objects.create_user(
            username='testdoctor',
            email='doctor@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith'
        )
        self.doctor = Doctor.objects.create(
            user=self.user,
            specialization=self.specialization,
            phone='9876543210',
            license_number='MD123456',
            experience_years=10,
            clinic_address='Medical Center',
            consultation_fee=500.00
        )
    
    def test_doctor_creation(self):
        self.assertEqual(self.doctor.user.username, 'testdoctor')
        self.assertEqual(self.doctor.specialization.name, 'Cardiology')
        self.assertEqual(self.doctor.experience_years, 10)
    
    def test_doctor_string_representation(self):
        expected_string = f"Dr. {self.user.first_name} {self.user.last_name}"
        self.assertEqual(str(self.doctor), expected_string)


class DoctorViewTest(TestCase):
    
    def test_doctor_login_page(self):
        response = self.client.get('/doctors/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'doctors/login.html')
    
    def test_doctor_register_page(self):
        response = self.client.get('/doctors/register/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'doctors/register.html')
