from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.exceptions import ValidationError

ROLE_CHOICES = [
    ('collaborateur', 'Collaborateur'),
    ('admin', 'Admin'),
    ('secretaire', 'Secrétaire'),
    ('prestataire', 'Prestataire')
]

SITE_CHOICES = [
    ('Danga', 'Danga'),
    ('Campus', 'Campus')
]

DEPARTEMENT_CHOICES = [
    ('Developpement', 'Développement'),
    ('Ressources Humaines', 'Ressources Humaines'),
    ('Comptabilite', 'Comptabilité'),
    ('Marketing', 'Marketing'),
    ('DATA', 'DATA'),
    ('Cybersecurite', 'Cybersécurité'),
    ('Infra', 'Infra'),
    ('Secretariat', 'Secrétariat'),
    ('Autres','Autres')
]

from django.contrib.auth.base_user import BaseUserManager

class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Utilisateur(AbstractUser):
    username = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='collaborateur')
    qid = models.CharField(max_length=100, blank=True)
    site = models.CharField(max_length=100, choices=SITE_CHOICES, default='Danga')
    departement = models.CharField(max_length=100, choices=DEPARTEMENT_CHOICES, default='Autres')  
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='utilisateurs_crees'  
    )
    is_updated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    updated_by = models.ForeignKey( 
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='utilisateurs_modifies'
    )
    deleted_by = models.ForeignKey( 
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='utilisateurs_supprimes'
    )
    theme_sombre = models.BooleanField(default=False)
    
    objects = UtilisateurManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['prenom', 'nom']

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['nom', 'prenom']

    def get_dashboard_url(self):
        role_dashboards = {
            'admin': 'admin_dashboard',
            'secretaire': 'secretaire_dashboard', 
            'prestataire': 'prestataire_dashboard'
        }
        return role_dashboards.get(self.role, 'collaborateur_dashboard')
    
    @property
    def has_admin_access(self):
        return self.role == 'admin' or self.is_superuser
    
    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.role} - {self.departement}"
    
    def clean(self):
        if self.role == 'admin' and not self.is_superuser:
            raise ValidationError("Les administrateurs doivent avoir le statut de superutilisateur.")
    
    def save(self, *args, **kwargs):
        if not self.pk:  
            self.is_updated = False
            self.is_deleted = False
            
            # Auto-set role to 'admin' for RH department by default
            if self.departement == 'RH' and self.role != 'admin':
                self.role = 'admin'
                if not self.is_superuser:
                    self.is_superuser = True
                    self.is_staff = True
        
        super().save(*args, **kwargs)

class Profile(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur, 
        on_delete=models.SET_NULL, null=True, blank=True,   
        related_name='profile'
    )
    telephone = models.CharField(max_length=20, blank=True)  
    
    def __str__(self):
        if self.utilisateur:
            return f"Profil de {self.utilisateur.prenom} {self.utilisateur.nom}"
        return "Profil sans utilisateur"
 
