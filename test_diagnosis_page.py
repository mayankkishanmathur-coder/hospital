#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from patients.models import Patient

# Create a test user and patient
try:
    # Try to get or create a test user
    user, created = User.objects.get_or_create(
        username='testpatient',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'Patient'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print('Created test user: testpatient / testpass123')
    else:
        user.set_password('testpass123')
        user.save()
        print('Updated test user password')
    
    # Ensure patient profile exists
    patient, p_created = Patient.objects.get_or_create(
        user=user,
        defaults={
            'date_of_birth': '1990-01-01',
            'phone': '1234567890',
            'address': '123 Test St'
        }
    )
    
    if p_created:
        print('Created patient profile')
    else:
        print('Patient profile already exists')
    
    # Now test the page access
    client = Client()
    login_success = client.login(username='testpatient', password='testpass123')
    print(f'\nLogin attempt: {login_success}')
    
    if login_success:
        response = client.get('/diagnosis/')
        print(f'Diagnosis page status: {response.status_code}')
        
        if response.status_code == 200:
            content = response.content.decode()
            
            checks = [
                ('diagnosisForm' in content, 'Diagnosis form'),
                ('Describe Your Symptoms' in content, 'Page title'),
                ('form-check' in content, 'Form checkboxes'),
                ('Analyze Symptoms' in content, 'Submit button'),
                ('Self-Diagnosis Portal' in content, 'Page heading'),
            ]
            
            print('\n✓ SUCCESS! Page loaded (HTTP 200). Elements found:')
            for check, label in checks:
                status = '✓' if check else '✗'
                print(f'  {status} {label}')
            
            num_fields = content.count('name="symptom_')
            print(f'\n  ℹ️  Total symptom fields: {num_fields}')
            
            # More detailed error checking
            if '<h1>' in content and 'Self-Diagnosis' in content:
                print('  ✓ Page header rendered correctly')
            
            if '<form' in content and 'POST' in content:
                print('  ✓ Form element present and configured for POST')
            
            if 'csrf' in content.lower():
                print('  ✓ CSRF token included')
                
            # Check for any Python/Django error pages (not just the word 'error')
            if 'Traceback' in content or 'TemplateDoesNotExist' in content:
                print('  ✗ ERROR: Found exception traceback in response!')
                print(response.content[response.content.find(b'Traceback'):response.content.find(b'Traceback')+500].decode())
            else:
                print('  ✓ No exception tracebacks found')
            
        elif response.status_code == 500:
            print('✗ ERROR: 500 Internal Server Error')
            # Try to find error details
            if b'TemplateSyntaxError' in response.content:
                print('  Found TemplateSyntaxError!')
                # Extract error message
                start = response.content.find(b'TemplateSyntaxError')
                print(f'  {response.content[start:start+200]}')
        else:
            print(f'Unexpected status: {response.status_code}')
    else:
        print('Login failed')
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
