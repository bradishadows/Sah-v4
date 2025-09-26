from django.urls import path
from . import views

app_name = 'plats'

urlpatterns = [
    # Vues pour les plats (accessibles à tous les utilisateurs authentifiés)
    path('', views.liste_plats, name='liste_plats'),
    path('<int:pk>/detail/', views.detail_plat, name='detail_plat'),
    
    # Vues admin pour les plats
    path('creer/', views.creer_plat, name='creer_plat'),
    path('<int:pk>/modifier/', views.modifier_plat, name='modifier_plat'),
    path('<int:pk>/supprimer/', views.supprimer_plat, name='supprimer_plat'),
    path('<int:pk>/activer-desactiver/', views.activer_desactiver_plat, name='activer_desactiver_plat'),
    
    # Vues pour les catégories (admin uniquement)
    path('categories/', views.liste_categories, name='liste_categories'),
    path('categories/creer/', views.creer_categorie, name='creer_categorie'),
    path('categories/<int:pk>/modifier/', views.modifier_categorie, name='modifier_categorie'),
    path('categories/<int:pk>/supprimer/', views.supprimer_categorie, name='supprimer_categorie'),
]
