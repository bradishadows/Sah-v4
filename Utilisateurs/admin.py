from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Profile

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('email', 'prenom', 'nom', 'role', 'site', 'departement', 'is_active')
    list_filter = ('role', 'site', 'departement', 'is_active')
    search_fields = ('email', 'prenom', 'nom')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('prenom', 'nom', 'role', 'site', 'departement', 'qid')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
        ('Préférences', {'fields': ('theme_sombre',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'prenom', 'nom', 'site', 'departement', 'password1', 'password2'),
        }),
    )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'telephone')
    search_fields = ('utilisateur__email', 'utilisateur__prenom', 'utilisateur__nom')