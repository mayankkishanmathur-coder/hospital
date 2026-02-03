import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.contrib.auth.models import User
from patients.models import Patient
from doctors.models import Doctor, DoctorSpecialization

print("\n" + "="*60)
print("Creating Sample Doctors and Patients")
print("="*60 + "\n")

# Create sample patients
print("Creating 4 sample patients...")
patients = [
    {'username': 'john_doe', 'email': 'john@hospital.com', 'name': 'John Doe', 'phone': '9876543210', 'address': '123 Main St', 'dob': '1990-05-15'},
    {'username': 'jane_smith', 'email': 'jane@hospital.com', 'name': 'Jane Smith', 'phone': '9876543211', 'address': '456 Oak Ave', 'dob': '1988-03-22'},
    {'username': 'michael_brown', 'email': 'michael@hospital.com', 'name': 'Michael Brown', 'phone': '9876543212', 'address': '789 Pine Rd', 'dob': '1985-07-10'},
    {'username': 'sarah_wilson', 'email': 'sarah@hospital.com', 'name': 'Sarah Wilson', 'phone': '9876543213', 'address': '321 Elm St', 'dob': '1992-11-18'},
]

for patient in patients:
    if not User.objects.filter(username=patient['username']).exists():
        user = User.objects.create_user(username=patient['username'], email=patient['email'], password='patient123')
        first_name, last_name = patient['name'].split()
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        Patient.objects.create(user=user, phone=patient['phone'], address=patient['address'], date_of_birth=patient['dob'])
        print(f"  ✓ {patient['name']}")

# Create sample doctors with different specializations
print("\nCreating 8 sample doctors...")
doctors = [
    {'username': 'dr_smith', 'email': 'dr.smith@hospital.com', 'name': 'Dr. Smith', 'phone': '9876543220', 'spec': 'Cardiology', 'license': 'LIC001', 'exp': 10, 'clinic': '100 Heart St', 'fee': 500},
    {'username': 'dr_patel', 'email': 'dr.patel@hospital.com', 'name': 'Dr. Patel', 'phone': '9876543221', 'spec': 'Neurology', 'license': 'LIC002', 'exp': 8, 'clinic': '200 Brain Ave', 'fee': 550},
    {'username': 'dr_johnson', 'email': 'dr.johnson@hospital.com', 'name': 'Dr. Johnson', 'phone': '9876543222', 'spec': 'Orthopedics', 'license': 'LIC003', 'exp': 12, 'clinic': '300 Bone St', 'fee': 450},
    {'username': 'dr_williams', 'email': 'dr.williams@hospital.com', 'name': 'Dr. Williams', 'phone': '9876543223', 'spec': 'Pediatrics', 'license': 'LIC004', 'exp': 6, 'clinic': '400 Kid Ave', 'fee': 400},
    {'username': 'dr_garcia', 'email': 'dr.garcia@hospital.com', 'name': 'Dr. Garcia', 'phone': '9876543224', 'spec': 'Psychiatry', 'license': 'LIC005', 'exp': 7, 'clinic': '500 Mind St', 'fee': 600},
    {'username': 'dr_miller', 'email': 'dr.miller@hospital.com', 'name': 'Dr. Miller', 'phone': '9876543225', 'spec': 'Dermatology', 'license': 'LIC006', 'exp': 9, 'clinic': '600 Skin Ave', 'fee': 350},
    {'username': 'dr_davis', 'email': 'dr.davis@hospital.com', 'name': 'Dr. Davis', 'phone': '9876543226', 'spec': 'ENT', 'license': 'LIC007', 'exp': 11, 'clinic': '700 Ear St', 'fee': 400},
    {'username': 'dr_robinson', 'email': 'dr.robinson@hospital.com', 'name': 'Dr. Robinson', 'phone': '9876543227', 'spec': 'Cardiology', 'license': 'LIC008', 'exp': 5, 'clinic': '800 Heart Ave', 'fee': 500},
]

for doctor in doctors:
    if not User.objects.filter(username=doctor['username']).exists():
        user = User.objects.create_user(username=doctor['username'], email=doctor['email'], password='doctor123')
        first_name, last_name = doctor['name'].split()
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        spec = DoctorSpecialization.objects.get(name=doctor['spec'])
        Doctor.objects.create(user=user, phone=doctor['phone'], specialization=spec, license_number=doctor['license'], 
                            experience_years=doctor['exp'], clinic_address=doctor['clinic'], consultation_fee=doctor['fee'])
        print(f"  ✓ {doctor['name']} - {doctor['spec']}")

print("\n" + "="*60)
print("LOGIN CREDENTIALS")
print("="*60)
print("\n📌 Admin Panel: http://localhost:8000/admin")
print("   Username: admin")
print("   Password: admin123")

print("\n👥 Patient Accounts:")
for patient in patients:
    print(f"   {patient['username']} / patient123")

print("\n👨‍⚕️ Doctor Accounts:")
for doctor in doctors:
    print(f"   {doctor['username']} / doctor123")

print("\n" + "="*60)
print("✓ Sample data created successfully!")
print("="*60 + "\n")
