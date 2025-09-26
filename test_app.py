#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from Utilisateurs.models import Utilisateur
from django.test import Client
from django.urls import reverse

def test_app():
    print("=== Testing SAH Analytics App ===")

    # Test 1: Check if we can create a user
    print("\n1. Testing user creation...")
    try:
        user = Utilisateur.objects.create(
            email='test@example.com',
            username='test@example.com',  # Since USERNAME_FIELD = 'email'
            prenom='Test',
            nom='User',
            role='collaborateur',
            site='Danga'
        )
        user.set_password('test123')
        user.save()
        print("✓ User created successfully")
    except Exception as e:
        print(f"✗ Error creating user: {e}")
        return

    # Test 2: Test login view
    print("\n2. Testing login view...")
    client = Client()
    try:
        response = client.get('/login/')
        if response.status_code == 200:
            print("✓ Login page loads successfully")
        else:
            print(f"✗ Login page failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error accessing login: {e}")

    # Test 3: Test authentication
    print("\n3. Testing authentication...")
    try:
        login_success = client.login(email='test@example.com', password='test123')
        if login_success:
            print("✓ Authentication successful")
        else:
            print("✗ Authentication failed")
    except Exception as e:
        print(f"✗ Error during authentication: {e}")

    # Test 4: Test dashboard redirect
    print("\n4. Testing dashboard redirect...")
    try:
        response = client.get('/dashboard/')
        if response.status_code in [200, 302]:
            print("✓ Dashboard accessible")
        else:
            print(f"✗ Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error accessing dashboard: {e}")

    print("\n=== Test Summary ===")
    print("Basic functionality tests completed.")

if __name__ == '__main__':
    test_app()
