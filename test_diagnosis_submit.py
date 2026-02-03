#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from patients.models import Patient
from diagnosis.models import Symptom

# Get or create test user
user, _ = User.objects.get_or_create(
    username='testpatient',
    defaults={
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Patient'
    }
)
user.set_password('testpass123')
user.save()

# Get or create patient profile
patient, _ = Patient.objects.get_or_create(
    user=user,
    defaults={
        'date_of_birth': '1990-01-01',
        'phone': '1234567890',
        'address': '123 Test St'
    }
)

# Get first 3 symptoms for testing
symptoms = Symptom.objects.filter(is_active=True)[:3]
print(f'Found {symptoms.count()} symptoms to test')

if symptoms.count() >= 1:
    client = Client()
    login_success = client.login(username='testpatient', password='testpass123')
    print(f'Login: {login_success}')
    
    if login_success:
        # Get the form page first to extract CSRF token
        response = client.get('/diagnosis/')
        print(f'Diagnosis page: {response.status_code}')
        
        # Extract CSRF token from response 
        import re
        csrf_match = re.search(r'csrfmiddlewaretoken[\'"]?\s*[:\']?\s*["\']([a-zA-Z0-9]+)["\']', response.content.decode())
        csrf_token = csrf_match.group(1) if csrf_match else None
        
        # Prepare form data with correct values for RadioSelect fields
        form_data = {}
        for symptom in symptoms:
            field_name = f'symptom_{symptom.id}'
            form_data[field_name] = 'yes'  # RadioSelect value for "Yes - Present"
        
        # Add CSRF token
        if csrf_token:
            form_data['csrfmiddlewaretoken'] = csrf_token
            print('✓ CSRF token extracted')
        
        print(f'\n✓ Form data prepared with {len(symptoms)} symptoms selected:')
        for symptom in symptoms:
            print(f'  - {symptom.name}')
        
        # Submit the form
        response = client.post('/diagnosis/', form_data)
        print(f'\nForm submission response: {response.status_code}')
        
        if response.status_code == 302:
            # Should redirect to results page
            redirect_url = response.url
            print(f'✓ Redirected to: {redirect_url}')
            
            # Follow redirect
            response = client.get(redirect_url)
            print(f'Results page status: {response.status_code}')
            
            if response.status_code == 200:
                content = response.content.decode()
                if 'Diagnosis Results' in content or 'predicted' in content.lower():
                    print('✓ Results page loaded successfully')
                    print('✓ Diagnosis predictions shown')
                else:
                    print('⚠️ Results page may not show predictions')
            elif response.status_code == 404:
                print('⚠️ Results page not found (expected if record ID not in URL)')
        elif response.status_code == 200:
            # Form had errors or redisplay
            content = response.content.decode()
            if 'error' in content.lower() and 'select' in content.lower():
                print('ℹ️ Form validation error - no symptoms selected')
            else:
                print('ℹ️ Form redisplayed (possible validation error)')
        else:
            print(f'Unexpected response: {response.status_code}')
            print(response.content[:500].decode())
else:
    print('No symptoms available for testing')
