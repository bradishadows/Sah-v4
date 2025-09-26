from django.urls import path
from . import views

urlpatterns = [
    # Vues pour collaborateurs
    path('mes-avis/', views.mes_avis, name='mes_avis'),
    path('donner-avis/<int:commande_id>/', views.donner_avis, name='donner_avis_commande'),
    path('donner-avis/plat/<int:plat_id>/', views.donner_avis, name='donner_avis_plat'),
    path('modifier-avis/<int:avis_id>/', views.modifier_avis, name='modifier_avis'),
    path('supprimer-avis/<int:avis_id>/', views.supprimer_avis, name='supprimer_avis'),
    path('notifications-avis/', views.notifications_avis, name='notifications_avis'),
    
    # Vues pour admin
    path('moderation/', views.moderation_avis, name='moderation_avis'),
    path('approuver-avis/<int:avis_id>/', views.approuver_avis, name='approuver_avis'),
    path('rejeter-avis/<int:avis_id>/', views.rejeter_avis, name='rejeter_avis'),
    path('statistiques/', views.statistiques_avis, name='statistiques_avis'),
    
    # Vues publiques
    path('avis-plats/', views.avis_plats, name='avis_plats'),
    path('avis-plats/<int:plat_id>/', views.avis_plats, name='avis_plat_detail'),
    
    # API
    path('api/avis-plat/<int:plat_id>/', views.api_avis_plat, name='api_avis_plat'),
    path('api/demande-avis/', views.api_demande_avis, name='api_demande_avis'),
]
