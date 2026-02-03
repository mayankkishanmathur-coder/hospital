import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.contrib.auth.models import User
from doctors.models import DoctorSpecialization

# Create superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("✓ Superuser 'admin' created with password 'admin123'")
else:
    print("✓ Superuser 'admin' already exists")

# Initialize specializations
specs = [
    'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Psychiatry',
    'Dermatology', 'ENT', 'Gastroenterology', 'Ophthalmology', 'Urology'
]

for spec in specs:
    DoctorSpecialization.objects.get_or_create(name=spec)
print(f"✓ {len(specs)} doctor specializations initialized")
