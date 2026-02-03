"""
Create sample data for testing the Hospital Appointment System.
Run this after migrations: python create_sample_data.py
"""

import os
import django
from datetime import date, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.contrib.auth.models import User
from patients.models import Patient
from doctors.models import Doctor, DoctorSpecialization
from appointments.models import Appointment


def create_sample_data():
    """Create sample data for testing."""
    
    print("\n" + "="*50)
    print("Creating Sample Data")
    print("="*50 + "\n")
    
    # Create specializations if they don't exist
    print("Creating specializations...")
    specs = {}
    spec_list = [
        ('Cardiology', 'Heart and blood vessel diseases'),
        ('Orthopedics', 'Bone and joint disorders'),
        ('General Medicine', 'General health and wellness'),
    ]
    
    for name, desc in spec_list:
        spec, created = DoctorSpecialization.objects.get_or_create(
            name=name,
            defaults={'description': desc}
        )
        specs[name] = spec
        if created:
            print(f"  ✓ Created: {name}")
        else:
            print(f"  - Already exists: {name}")
    
    # Create sample patients
    print("\nCreating sample patients...")
    patient_data = [
        {
            'username': 'john_patient',
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'testpass123',
            'phone': '9876543210',
            'address': '123 Main Street, New York',
            'date_of_birth': date(1985, 5, 15),
        },
        {
            'username': 'jane_patient',
            'email': 'jane@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'password': 'testpass123',
            'phone': '9876543211',
            'address': '456 Oak Avenue, Boston',
            'date_of_birth': date(1990, 8, 20),
        },
    ]
    
    patients = []
    for data in patient_data:
        username = data['username']
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
            )
            patient = Patient.objects.create(
                user=user,
                phone=data['phone'],
                address=data['address'],
                date_of_birth=data['date_of_birth'],
            )
            patients.append(patient)
            print(f"  ✓ Created patient: {data['first_name']} {data['last_name']}")
        else:
            patient = Patient.objects.get(user__username=username)
            patients.append(patient)
            print(f"  - Already exists: {data['first_name']} {data['last_name']}")
    
    # Create sample doctors
    print("\nCreating sample doctors...")
    doctor_data = [
        {
            'username': 'dr_smith',
            'email': 'dr.smith@example.com',
            'first_name': 'Robert',
            'last_name': 'Smith',
            'password': 'testpass123',
            'specialization': 'Cardiology',
            'phone': '1234567890',
            'license_number': 'MD001234',
            'experience_years': 15,
            'clinic_address': 'Heart Care Clinic, 789 Medical Lane',
            'consultation_fee': 500.00,
        },
        {
            'username': 'dr_williams',
            'email': 'dr.williams@example.com',
            'first_name': 'Sarah',
            'last_name': 'Williams',
            'password': 'testpass123',
            'specialization': 'Orthopedics',
            'phone': '1234567891',
            'license_number': 'MD001235',
            'experience_years': 12,
            'clinic_address': 'Bone & Joint Clinic, 321 Care Road',
            'consultation_fee': 400.00,
        },
        {
            'username': 'dr_johnson',
            'email': 'dr.johnson@example.com',
            'first_name': 'Michael',
            'last_name': 'Johnson',
            'password': 'testpass123',
            'specialization': 'General Medicine',
            'phone': '1234567892',
            'license_number': 'MD001236',
            'experience_years': 10,
            'clinic_address': 'General Health Clinic, 555 Wellness Ave',
            'consultation_fee': 300.00,
        },
        {
            'username': 'dr_brown',
            'email': 'dr.brown@example.com',
            'first_name': 'Emily',
            'last_name': 'Brown',
            'password': 'testpass123',
            'specialization': 'Cardiology',
            'phone': '1234567893',
            'license_number': 'MD001237',
            'experience_years': 8,
            'clinic_address': 'Advanced Cardiac Care, 111 Heart St',
            'consultation_fee': 550.00,
        },
    ]
    
    doctors = []
    for data in doctor_data:
        username = data['username']
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
            )
            doctor = Doctor.objects.create(
                user=user,
                specialization=specs[data['specialization']],
                phone=data['phone'],
                license_number=data['license_number'],
                experience_years=data['experience_years'],
                clinic_address=data['clinic_address'],
                consultation_fee=data['consultation_fee'],
            )
            doctors.append(doctor)
            print(f"  ✓ Created doctor: Dr. {data['first_name']} {data['last_name']} ({data['specialization']})")
        else:
            doctor = Doctor.objects.get(user__username=username)
            doctors.append(doctor)
            print(f"  - Already exists: Dr. {data['first_name']} {data['last_name']}")
    
    # Create sample appointments
    print("\nCreating sample appointments...")
    if patients and doctors:
        appointments_to_create = [
            {
                'patient': patients[0],
                'doctor': doctors[0],
                'appointment_date': date(2026, 2, 10),
                'appointment_time': time(10, 30),
                'reason': 'Regular cardiac checkup',
                'status': 'pending',
            },
            {
                'patient': patients[0],
                'doctor': doctors[1],
                'appointment_date': date(2026, 2, 15),
                'appointment_time': time(14, 0),
                'reason': 'Knee pain consultation',
                'status': 'approved',
                'notes': 'Bring X-ray reports',
            },
            {
                'patient': patients[1],
                'doctor': doctors[2],
                'appointment_date': date(2026, 2, 20),
                'appointment_time': time(9, 0),
                'reason': 'General health checkup',
                'status': 'pending',
            },
        ]
        
        for apt_data in appointments_to_create:
            # Check if similar appointment already exists
            existing = Appointment.objects.filter(
                patient=apt_data['patient'],
                appointment_date=apt_data['appointment_date'],
                appointment_time=apt_data['appointment_time']
            ).exists()
            
            if not existing:
                apt = Appointment.objects.create(
                    patient=apt_data['patient'],
                    doctor=apt_data['doctor'],
                    appointment_date=apt_data['appointment_date'],
                    appointment_time=apt_data['appointment_time'],
                    reason=apt_data['reason'],
                    status=apt_data['status'],
                )
                if apt_data.get('notes'):
                    apt.notes = apt_data['notes']
                    apt.save()
                print(f"  ✓ Created appointment: {apt_data['patient'].user.first_name} with Dr. {apt_data['doctor'].user.first_name}")
            else:
                print(f"  - Appointment already exists")
    
    print("\n" + "="*50)
    print("Sample Data Created Successfully!")
    print("="*50 + "\n")
    
    print("Test Credentials:")
    print("-" * 50)
    print("\nPatient Accounts:")
    for data in patient_data:
        print(f"  Username: {data['username']}")
        print(f"  Password: {data['password']}")
        print()
    
    print("Doctor Accounts:")
    for data in doctor_data:
        print(f"  Username: {data['username']}")
        print(f"  Password: {data['password']}")
        print()
    
    print("="*50)


if __name__ == '__main__':
    try:
        create_sample_data()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
