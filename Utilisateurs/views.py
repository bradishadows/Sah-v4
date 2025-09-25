# Utilisateurs/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.contrib import messages

from .forms import EmailAuthenticationForm, CustomUserCreationForm, CustomPasswordResetForm
from .models import Utilisateur

def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
    
    if request.method == 'POST':
        form = EmailAuthenticationForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', False)
            
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                
                if not remember_me:
                    request.session.set_expiry(0)
                
                messages.success(request, f'Bienvenue {user.prenom} !')
                return redirect(user.get_dashboard_url())
            else:
                messages.error(request, 'Email ou mot de passe incorrect.')
    else:
        form = EmailAuthenticationForm()
    
    return render(request, 'Utilisateurs/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Compte créé avec succès ! Bienvenue {user.prenom} !')
            return redirect(user.get_dashboard_url())
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'Utilisateurs/register.html', {'form': form})

# Dashboards spécifiques par rôle
@login_required
def dashboard_view(request):
    return redirect(request.user.get_dashboard_url())

@login_required
def admin_dashboard_view(request):
    if request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')
    return render(request, 'Utilisateurs/dashboards/admin_dashboard.html')

@login_required
def prestataire_dashboard_view(request):
    if request.user.role != 'prestataire':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')
    return render(request, 'Utilisateurs/dashboards/prestataire_dashboard.html')

@login_required
def secretaire_dashboard_view(request):
    if request.user.role != 'secretaire':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')
    return render(request, 'Utilisateurs/dashboards/secretaire_dashboard.html')

@login_required
def collaborateur_dashboard_view(request):
    return render(request, 'Utilisateurs/dashboards/collaborateur_dashboard.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')
def admin_menus(request):
    return render(request, '')
def admin_users(request):
    return render(request, '')
def admin_orders(request):
    return render(request, '')
def admin_reports(request):
    return render(request, '')
def admin_menus_create(request):
    return render(request, '')
def admin_notifications(request):
    return render(request, '')
@login_required
def profile_view(request):
    return render(request, 'Utilisateurs/profile.html')

@login_required
def toggle_theme_view(request):
    if request.method == 'POST':
        user = request.user
        user.theme_sombre = not user.theme_sombre
        user.save()
    return redirect(request.user.get_dashboard_url())

@login_required
def menus_semaine_view(request):
    return render(request, "menus/menus_semaine.html")

@login_required
def historique_commandes_view(request):
    return render(request, 'historique/historique_commandes.html')

@login_required
def donner_avis(request):
    return render(request, 'avis/donner_avis.html')

@login_required
def mes_avis_view(request):
    return render(request, 'avis/mes_avis.html')

@login_required
def commander_plat(request):
    return render(request, 'commandes/commander_plat.html')


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'Utilisateurs/password_reset.html'
    email_template_name = 'Utilisateurs/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'Utilisateurs/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'Utilisateurs/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'Utilisateurs/password_reset_complete.html'