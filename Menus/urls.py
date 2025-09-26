from django.urls import path
from . import views

app_name = 'menus'

urlpatterns = [
    # Vues pour collaborateurs
    path('semaine/', views.menus_semaine, name='menus_semaine'),
    path('commander/<int:menu_id>/', views.commander_menu, name='commander_menu'),
    
    # Vues pour admin
    path('admin/dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('admin/gerer-semaine/', views.gerer_menus_semaine, name='gerer_menus_semaine'),
    path('admin/modifier/<int:menu_id>/', views.modifier_menu, name='modifier_menu'),
    path('admin/suivi-commandes/', views.suivi_commandes, name='suivi_commandes'),
    
    # Vues pour prestataire
    path('prestataire/dashboard/', views.dashboard_prestataire, name='dashboard_prestataire'),
    path('prestataire/consolidation/', views.consolidation_commandes, name='consolidation_commandes'),
    path('prestataire/gerer-semaine/', views.prestataire_gerer_menus_semaine, name='prestataire_gerer_menus_semaine'),
    path('prestataire/menu/<int:menu_id>/', views.create_or_edit_menu_prestataire, name='create_or_edit_menu_prestataire'),
    
    # API
    path('api/menus-a-publier/', views.api_menus_a_publicr, name='api_menus_a_publier'),
    path('api/commandes-limite/', views.api_commandes_limite, name='api_commandes_limite'),
]
