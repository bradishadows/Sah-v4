#!/usr/bin/env python
"""
Test script to verify menu access for different user roles
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def test_menu_access():
    """Test that all authenticated users can access menu viewing"""
    client = Client()

    # Test URLs that should be accessible to all authenticated users
    menu_urls = [
        'menus_semaine',  # View weekly menus
    ]

    # Create test users for different roles
    roles = ['collaborateur', 'admin', 'secretaire', 'prestataire']

    for role in roles:
        # Create or get user
        user, created = User.objects.get_or_create(
            username=f'test_{role}',
            defaults={
                'email': f'test_{role}@example.com',
                'role': role,
                'prenom': f'Test{role.title()}',
                'nom': f'User{role.title()}',
                'site': 'Danga'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()

        # Login
        client.login(username=f'test_{role}', password='testpass123')

        # Test menu access
        for url_name in menu_urls:
            try:
                url = reverse(url_name)
                response = client.get(url)
                print(f"✓ {role}: {url_name} - Status {response.status_code}")
                if response.status_code != 200:
                    print(f"  Error: {response.content.decode()[:200]}...")
            except Exception as e:
                print(f"✗ {role}: {url_name} - Error: {e}")

        # Logout
        client.logout()
        print()

if __name__ == '__main__':
    test_menu_access()
