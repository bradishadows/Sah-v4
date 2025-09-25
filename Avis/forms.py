from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db import models
import json
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import re
from django.forms.models import model_to_dict
from datetime import datetime, timedelta

from Utilisateurs.models import DEPARTEMENT_CHOICES, ROLE_CHOICES, SITE_CHOICES, Utilisateur


app_name =  "utilisateurs"

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if not hasattr(request.user, 'role') or request.user.role != 'admin':
            return JsonResponse({'error': 'Permission refusée. Admin requis'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

# Décorateur pour vérifier les droits prestataire
def prestataire_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if not hasattr(request.user, 'role') or request.user.role != 'prestataire':
            return JsonResponse({'error': 'Permission refusée. Prestataire requis'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

# Validation des données utilisateur
def validate_utilisateur_data(data, is_update=False):
    errors = {}
    
    # Validation des champs requis pour la création
    if not is_update:
        required_fields = ['nom', 'prenom', 'email', 'mot_de_passe', 'qid', 'site', 'departement']
        for field in required_fields:
            if field not in data or not data[field]:
                errors[field] = 'Ce champ est requis'
    
    # Validation email
    if 'email' in data:
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
            errors['email'] = 'Format d\'email invalide'
        elif not data['email'].lower().endswith('@sahanalytics.com'):
            errors['email'] = 'Seules les adresses Professionnelles sont autorisées'
        elif Utilisateur.objects.filter(email=data['email'], is_deleted=False).exclude(id=data.get('id')).exists():
            errors['email'] = 'Cet email est déjà utilisé'
    
    # Validation des choix
    if 'role' in data and data['role'] not in [choice[0] for choice in ROLE_CHOICES]:
        errors['role'] = 'Rôle invalide'
    
    if 'site' in data and data['site'] not in [choice[0] for choice in SITE_CHOICES]:
        errors['site'] = 'Site invalide'
    
    if 'departement' in data and data['departement'] not in [choice[0] for choice in DEPARTEMENT_CHOICES]:
        errors['departement'] = 'Département invalide'
    
    # Validation mot de passe
    if 'mot_de_passe' in data and len(data['mot_de_passe']) < 8:
        errors['mot_de_passe'] = 'Le mot de passe doit contenir au moins 8 caractères'
    
    return errors

# Gestion de la connexion
@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('mot_de_passe')
        
        if not email or not password:
            return JsonResponse({'error': 'Email et mot de passe requis'}, status=400)
        
        try:
            user = Utilisateur.objects.get(email=email, is_deleted=False)
        except Utilisateur.DoesNotExist:
            return JsonResponse({'error': 'Utilisateur non trouvé'}, status=404)
        
        if check_password(password, user.mot_de_passe):
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            return JsonResponse({
                'message': 'Connexion réussie',
                'user': {
                    'id': user.id,
                    'nom': user.nom,
                    'prenom': user.prenom,
                    'email': user.email,
                    'role': user.role,
                    'site': user.site,
                    'departement': user.departement
                }
            })
        else:
            return JsonResponse({'error': 'Mot de passe incorrect'}, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Données JSON invalides'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Gestion de la déconnexion
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Déconnexion réussie'})

# Récupérer l'utilisateur courant
@csrf_exempt
@require_http_methods(["GET"])
@login_required
def Recuperer_utilisateur_view(request):
    return JsonResponse({
        'id': request.user.id,
        'nom': request.user.nom,
        'prenom': request.user.prenom,
        'email': request.user.email,
        'role': request.user.role,
        'site': request.user.site,
        'departement': request.user.departement
    })
