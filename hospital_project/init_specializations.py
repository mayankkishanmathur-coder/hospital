"""
Initialize database with doctor specializations.
Run this after migrations: python init_specializations.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from doctors.models import DoctorSpecialization

# List of medical specializations
SPECIALIZATIONS = [
    {
        'name': 'Cardiology',
        'description': 'Heart and blood vessel diseases. Diagnoses and treats heart conditions, arrhythmias, and hypertension.'
    },
    {
        'name': 'Orthopedics',
        'description': 'Bone and joint disorders. Specializes in treating injuries, arthritis, and musculoskeletal conditions.'
    },
    {
        'name': 'General Medicine',
        'description': 'General health and wellness. Provides comprehensive healthcare for adults.'
    },
    {
        'name': 'Pediatrics',
        'description': 'Child health and care. Specializes in treating children and newborns.'
    },
    {
        'name': 'Dermatology',
        'description': 'Skin diseases. Treats skin conditions, allergies, and cosmetic dermatology.'
    },
    {
        'name': 'Neurology',
        'description': 'Nervous system disorders. Treats epilepsy, migraines, and neurological conditions.'
    },
    {
        'name': 'Psychiatry',
        'description': 'Mental health and behavioral disorders. Treats depression, anxiety, and other mental health conditions.'
    },
    {
        'name': 'Ophthalmology',
        'description': 'Eye health and vision care. Diagnoses and treats eye diseases and vision problems.'
    },
    {
        'name': 'Dentistry',
        'description': 'Oral health and dental care. Provides preventive, cosmetic, and restorative dental services.'
    },
    {
        'name': 'ENT (Otolaryngology)',
        'description': 'Ear, nose, and throat. Treats hearing, balance, and respiratory conditions.'
    },
]

def initialize_specializations():
    """Create doctor specializations in the database."""
    print("Initializing doctor specializations...")
    print("-" * 50)
    
    created_count = 0
    existing_count = 0
    
    for spec_data in SPECIALIZATIONS:
        spec, created = DoctorSpecialization.objects.get_or_create(
            name=spec_data['name'],
            defaults={'description': spec_data['description']}
        )
        
        if created:
            print(f"✓ Created: {spec_data['name']}")
            created_count += 1
        else:
            print(f"- Already exists: {spec_data['name']}")
            existing_count += 1
    
    print("-" * 50)
    print(f"Total created: {created_count}")
    print(f"Already existed: {existing_count}")
    print(f"Total specializations: {created_count + existing_count}")
    print("\nDoctor specializations initialized successfully!")

if __name__ == '__main__':
    initialize_specializations()
