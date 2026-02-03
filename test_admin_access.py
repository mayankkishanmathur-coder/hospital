#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Test admin access
client = Client()

# Try to access admin page
response = client.get('/admin/')
print(f'Admin page (without auth): {response.status_code}')

# Try to login
login_success = client.login(username='admin', password='admin123')
print(f'Admin login: {login_success}')

if login_success:
    # Try to access admin page after login
    response = client.get('/admin/')
    print(f'Admin page (with auth): {response.status_code}')
    
    if response.status_code == 200:
        content = response.content.decode()
        checks = [
            ('django' in content.lower(), 'Django admin interface'),
            ('site administration' in content.lower(), 'Site administration title'),
            ('patient' in content.lower(), 'Patient model'),
            ('doctor' in content.lower(), 'Doctor model'),
        ]
        
        print('\nAdmin page elements:')
        for check, label in checks:
            status = '✓' if check else '✗'
            print(f'  {status} {label}')
    elif response.status_code == 302:
        print('Redirected (check if logged in properly)')
    else:
        print(f'Unexpected status: {response.status_code}')
else:
    print('Login failed')
    user = User.objects.get(username='admin')
    print(f'User exists: {user}')
    print(f'User is_staff: {user.is_staff}')
    print(f'User is_superuser: {user.is_superuser}')
