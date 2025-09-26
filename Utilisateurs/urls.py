from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentification
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('toggle-theme/', views.toggle_theme_view, name='toggle_theme'),
    path('donner_avis/', views.donner_avis, name='donner_avis'),
    
    path('admin_menus/', views.admin_menus, name='admin_menus'),
    path('admin_users/', views.admin_users, name='admin_users'),
    path('admin_users/create/', views.create_user, name='create_user'),
    path('admin_users/update/<int:user_id>/', views.update_user, name='update_user'),
    path('admin_users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin_orders/', views.admin_orders, name='admin_orders'),
    path('admin_reports/', views.admin_reports, name='admin_reports'),
    path('admin_menus_create/', views.admin_menus_create, name='admin_menus_create'),
    
    path('admin_notifications/', views.admin_notifications, name='admin_notifications'),
    path('admin_reviews/', views.admin_reviews, name='admin_reviews'),
    # Dashboards par rôle
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('dashboard/prestataire/', views.prestataire_dashboard_view, name='prestataire_dashboard'),
    path('dashboard/secretaire/', views.secretaire_dashboard_view, name='secretaire_dashboard'),
    path('dashboard/collaborateur/', views.collaborateur_dashboard_view, name='collaborateur_dashboard'),
    
    # Réinitialisation mot de passe
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profile/', views.profile_view, name='profile'),
    path("menus-semaine/", views.menus_semaine_view, name="menus_semaine"),
    path('historique/historique_commandes/',views.historique_commandes_view, name='historique_commandes'),
    path('avis/mes_avis/',views.mes_avis_view, name='mes_avis')
]