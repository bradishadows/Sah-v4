from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test

def role_required(required_roles):

    def check_roles(user):
        return user.is_authenticated and user.role in required_roles
    return user_passes_test(check_roles, login_url='login')

def admin_required(view_func):
    return role_required(['admin'])(view_func)

def prestataire_required(view_func):
    return role_required(['prestataire'])(view_func)

def secretaire_required(view_func):
    return role_required(['secretaire'])(view_func)