from django.urls import path
from . import views

app_name = 'commandes'

urlpatterns = [
    # Vues pour collaborateurs
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),
    path('commander/<int:menu_id>/', views.commander_plat, name='commander_plat'),
    path('modifier/<int:commande_id>/', views.modifier_commande, name='modifier_commande'),
    path('annuler/<int:commande_id>/', views.annuler_commande, name='annuler_commande'),
    
    # Vues pour admin
    path('admin/gestion/', views.gestion_commandes_admin, name='gestion_commandes_admin'),
    path('admin/modifier-statut/<int:commande_id>/', views.modifier_statut_commande, name='modifier_statut_commande'),
    path('admin/api/stats/', views.api_statistiques_commandes, name='api_statistiques_commandes'),
    
    # Vues pour prestataire
    path('prestataire/jour/', views.commandes_prestataire, name='commandes_prestataire'),
    path('prestataire/preparation/', views.preparation_commandes, name='preparation_commandes'),
]
