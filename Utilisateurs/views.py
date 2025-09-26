# Utilisateurs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone

from .forms import EmailAuthenticationForm, CustomUserCreationForm, CustomPasswordResetForm, UserSearchForm, AdminUserUpdateForm
from .models import Utilisateur

def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse(request.user.get_dashboard_url()))

    form = EmailAuthenticationForm()
    register_form = CustomUserCreationForm()

    if request.method == 'POST':
        # Check which form was submitted
        if 'username' in request.POST:  # Login form
            form = EmailAuthenticationForm(data=request.POST)
            if form.is_valid():
                email = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                remember_me = form.cleaned_data.get('remember_me', False)

                user = authenticate(request, username=email, password=password)

                if user is not None:
                    login(request, user)

                    if not remember_me:
                        request.session.set_expiry(0)

                    messages.success(request, f'Bienvenue {user.prenom} !')
                    return redirect(reverse(user.get_dashboard_url()))
                else:
                    messages.error(request, 'Email ou mot de passe incorrect.')
        elif 'prenom' in request.POST:  # Register form
            register_form = CustomUserCreationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                messages.success(request, f'Compte créé avec succès ! Bienvenue {user.prenom} !')
                return redirect(reverse(user.get_dashboard_url()))

    return render(request, 'utilisateurs/login.html', {
        'form': form,
        'register_form': register_form
    })

def register_view(request):
    if request.user.is_authenticated:
        return redirect(reverse(request.user.get_dashboard_url()))
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Compte créé avec succès ! Bienvenue {user.prenom} !')
            return redirect(reverse(user.get_dashboard_url()))
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'utilisateurs/register.html', {'form': form})

# Dashboards spécifiques par rôle
@login_required
def dashboard_view(request):
    return redirect(reverse(request.user.get_dashboard_url()))

@login_required
def admin_dashboard_view(request):
    if request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')

    from datetime import datetime, timedelta
    from django.db.models import Count, Avg, Q
    from Menus.models import Menu
    from Commandes.models import Commande
    from Avis.models import Avis
    from Plats.models import Plat

    # Date actuelle et semaine courante
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Lundi
    end_of_week = start_of_week + timedelta(days=6)  # Dimanche

    # Statistiques générales
    utilisateurs_actifs = Utilisateur.objects.filter(is_active=True).count()
    commandes_semaine = Commande.objects.filter(
        created_at__date__gte=start_of_week,
        created_at__date__lte=end_of_week,
        is_deleted=False
    ).count()

    commandes_aujourdhui = Commande.objects.filter(
        created_at__date=today,
        is_deleted=False
    ).count()

    # Calcul des taux de participation
    total_utilisateurs = Utilisateur.objects.filter(is_active=True).count()
    participation_prevue = commandes_semaine
    taux_participation = round((participation_prevue / total_utilisateurs * 100), 1) if total_utilisateurs > 0 else 0

    # Avis moyen
    avis_semaine = Avis.objects.filter(
        date_creation__date__gte=start_of_week,
        date_creation__date__lte=end_of_week
    )
    avis_moyen = avis_semaine.aggregate(avg_note=Avg('note'))['avg_note'] or 0
    avis_moyen = round(avis_moyen, 1)
    nombre_avis = avis_semaine.count()

    # Évolution (comparaison avec semaine précédente)
    start_last_week = start_of_week - timedelta(days=7)
    end_last_week = end_of_week - timedelta(days=7)

    utilisateurs_actifs_last_week = Utilisateur.objects.filter(
        date_joined__date__lte=end_last_week,
        is_active=True
    ).count()

    commandes_last_week = Commande.objects.filter(
        created_at__date__gte=start_last_week,
        created_at__date__lte=end_last_week,
        is_deleted=False
    ).count()

    evolution_utilisateurs = ((utilisateurs_actifs - utilisateurs_actifs_last_week) / utilisateurs_actifs_last_week * 100) if utilisateurs_actifs_last_week > 0 else 0
    evolution_commandes = ((commandes_semaine - commandes_last_week) / commandes_last_week * 100) if commandes_last_week > 0 else 0

    # Menus de la semaine
    menus_semaine = Menu.objects.filter(
        date__gte=start_of_week,
        date__lte=end_of_week,
        est_publie=True
    ).select_related().order_by('date')

    # Ajouter le nombre de commandes pour chaque menu
    for menu in menus_semaine:
        menu.nombre_commandes = Commande.objects.filter(
            menu=menu,
            is_deleted=False
        ).count()

    # Plats populaires (top 5)
    plats_populaires = []
    plats_with_counts = Commande.objects.filter(
        created_at__date__gte=start_of_week - timedelta(days=30),  # Dernier mois
        is_deleted=False
    ).values('plat__nom').annotate(
        commandes=Count('id')
    ).order_by('-commandes')[:5]

    total_commandes_plats = sum(plat['commandes'] for plat in plats_with_counts)
    for plat_data in plats_with_counts:
        popularite = round((plat_data['commandes'] / total_commandes_plats * 100), 1) if total_commandes_plats > 0 else 0
        plats_populaires.append({
            'nom': plat_data['plat__nom'],
            'commandes': plat_data['commandes'],
            'popularite': popularite
        })

    # Avis récents (5 derniers)
    avis_recents = Avis.objects.select_related(
        'utilisateur', 'commande__plat'
    ).order_by('-date_creation')[:5]

    # Actions rapides - données pour les liens
    admin_actions = {
        'utilisateurs': utilisateurs_actifs,
        'commandes': commandes_semaine,
    }

    context = {
        'stats': {
            'utilisateurs_actifs': utilisateurs_actifs,
            'evolution_utilisateurs': round(evolution_utilisateurs, 1),
            'commandes_semaine': commandes_semaine,
            'commandes_aujourdhui': commandes_aujourdhui,
            'evolution_commandes': round(evolution_commandes, 1),
            'taux_participation': taux_participation,
            'participation_prevue': participation_prevue,
            'utilisateurs_actifs': utilisateurs_actifs,
            'avis_moyen': avis_moyen,
            'nombre_avis': nombre_avis,
            'plats_populaires': plats_populaires,
        },
        'semaine_courante': start_of_week,
        'menus_semaine': menus_semaine,
        'avis_recents': avis_recents,
        'admin_actions': admin_actions,
    }

    return render(request, 'utilisateurs/dashboards/admin_dashboard.html', context)

@login_required
def prestataire_dashboard_view(request):
    if request.user.role != 'prestataire':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')

    from datetime import datetime, timedelta
    from Menus.models import Menu, MenuPlat
    from Commandes.models import Commande
    from Plats.models import Plat

    # Date actuelle et semaine courante
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Lundi
    end_of_week = start_of_week + timedelta(days=6)  # Dimanche

    # Statistiques générales
    commandes_semaine = Commande.objects.filter(
        created_at__date__gte=start_of_week,
        created_at__date__lte=end_of_week,
        is_deleted=False
    ).count()

    sites_actifs = Menu.objects.filter(
        date__gte=start_of_week,
        date__lte=end_of_week,
        est_publie=True
    ).values('site').distinct().count()

    plats_proposes = Plat.objects.filter(est_actif=True).count()

    # Jours avant limite (menus avec deadline proche)
    menus_limite = Menu.objects.filter(
        est_publie=True,
        date_limite_commande__lte=timezone.now() + timedelta(hours=24),
        date_limite_commande__gte=timezone.now()
    ).count()

    # Évolution des commandes (dernières 5 semaines)
    evolution_data = []
    for i in range(4, -1, -1):
        week_start = start_of_week - timedelta(days=i*7)
        week_end = week_start + timedelta(days=6)
        count = Commande.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=week_end,
            is_deleted=False
        ).count()
        evolution_data.append({
            'semaine': f'S{i+1}',
            'count': count
        })

    # Consolidation par site
    consolidation_site = {}
    sites = ['Danga', 'Campus']
    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi']

    for site in sites:
        menus_site = Menu.objects.filter(
            date__gte=start_of_week,
            date__lte=end_of_week,
            site=site,
            est_publie=True
        )

        consolidation_site[site] = {
            'total_commandes': 0,
            'details_par_jour': {}
        }

        for jour in jours:
            menus_jour = menus_site.filter(jour=jour)
            if menus_jour.exists():
                menu = menus_jour.first()
                total_jour = MenuPlat.objects.filter(menu=menu).aggregate(
                    total=Sum('quantite_commandee')
                )['total'] or 0
                consolidation_site[site]['details_par_jour'][jour] = total_jour
                consolidation_site[site]['total_commandes'] += total_jour
            else:
                consolidation_site[site]['details_par_jour'][jour] = 0

    # Commandes à traiter (en attente ou confirmées)
    commandes_a_traiter = Commande.objects.filter(
        statut__in=['en_attente', 'confirmee'],
        is_deleted=False
    ).select_related('utilisateur', 'plat', 'menu').order_by('menu__date', 'created_at')[:10]

    # Menus de la semaine
    menus_semaine = Menu.objects.filter(
        date__gte=start_of_week,
        date__lte=end_of_week,
        est_publie=True
    ).select_related().order_by('date')

    # Ajouter le nombre de commandes pour chaque menu
    for menu in menus_semaine:
        menu.nombre_commandes = MenuPlat.objects.filter(menu=menu).aggregate(
            total=Sum('quantite_commandee')
        )['total'] or 0

    context = {
        'stats': {
            'commandes_semaine': commandes_semaine,
            'sites_actifs': sites_actifs,
            'plats_proposes': plats_proposes,
            'menus_limite': menus_limite,
        },
        'evolution_data': evolution_data,
        'consolidation_site': consolidation_site,
        'commandes_a_traiter': commandes_a_traiter,
        'menus_semaine': menus_semaine,
        'semaine_courante': start_of_week,
        'sites': sites,
        'jours': jours,
    }
    return render(request, 'utilisateurs/dashboards/prestataire_dashboard.html', context)

@login_required
def secretaire_dashboard_view(request):
    if request.user.role != 'secretaire':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')

    from datetime import datetime, timedelta
    from Commandes.models import Commande
    from Avis.models import Avis
    from Menus.models import Menu

    # Statistiques générales
    total_users = Utilisateur.objects.filter(is_active=True).count()
    pending_notifications = 0  # À implémenter avec un vrai système de notifications

    # Commandes récentes (dernières 24h)
    recent_orders = Commande.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24),
        is_deleted=False
    ).count()

    # Approbations en attente (avis non approuvés)
    pending_approvals = Avis.objects.filter(est_approuve=False).count()

    # Notifications récentes (simulées pour l'instant)
    notifications = [
        {
            'message': 'Nouveaux menus à vérifier pour la semaine prochaine',
            'created_at': timezone.now() - timedelta(hours=2),
        },
        {
            'message': 'Rapport mensuel disponible',
            'created_at': timezone.now() - timedelta(hours=5),
        },
        {
            'message': 'Rappel: réunion équipe demain',
            'created_at': timezone.now() - timedelta(days=1),
        },
    ]

    # Activité récente (dernières actions)
    recent_activities = [
        {
            'description': 'Nouveau menu créé pour lundi',
            'timestamp': timezone.now() - timedelta(hours=1),
            'initials': 'AD',
        },
        {
            'description': 'Utilisateur ajouté au système',
            'timestamp': timezone.now() - timedelta(hours=3),
            'initials': 'JS',
        },
        {
            'description': 'Commande annulée par l\'utilisateur',
            'timestamp': timezone.now() - timedelta(hours=6),
            'initials': 'MC',
        },
    ]

    context = {
        'total_users': total_users,
        'pending_notifications': pending_notifications,
        'recent_orders': recent_orders,
        'pending_approvals': pending_approvals,
        'notifications': notifications,
        'recent_activities': recent_activities,
    }

    return render(request, 'utilisateurs/dashboards/secretaire_dashboard.html', context)

@login_required
def collaborateur_dashboard_view(request):
    from datetime import datetime, timedelta
    from Menus.models import Menu
    from Commandes.models import Commande
    from Avis.models import Avis

    # Obtenir la semaine actuelle (lundi à dimanche)
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Lundi
    end_of_week = start_of_week + timedelta(days=6)  # Dimanche

    # Récupérer les menus de la semaine pour le site de l'utilisateur
    menus_semaine = Menu.objects.filter(
        date__gte=start_of_week,
        date__lte=end_of_week,
        site=request.user.site,
        est_publie=True
    ).select_related('menuplat_set__plat').order_by('date', 'jour')

    # Grouper par jour
    menus_par_jour = {}
    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    for jour in jours:
        menus_jour = menus_semaine.filter(jour=jour)
        if menus_jour.exists():
            menu = menus_jour.first()
            # Vérifier si l'utilisateur a déjà commandé pour ce menu
            commande_existante = Commande.objects.filter(
                utilisateur=request.user,
                menu=menu,
                is_deleted=False
            ).exists()
            plats = menu.menuplat_set.select_related('plat').all()
            est_aujourdhui = menu.date == today
            est_futur = menu.date > today
            est_passe = menu.date < today
            menus_par_jour[jour] = {
                'menu': menu,
                'commande_existante': commande_existante,
                'plats': plats,
                'est_aujourdhui': est_aujourdhui,
                'est_futur': est_futur,
                'est_passe': est_passe,
                'date': menu.date
            }
        else:
            menus_par_jour[jour] = None

    # Commandes récentes (dernières 5)
    commandes_recentes = Commande.objects.filter(
        utilisateur=request.user,
        is_deleted=False
    ).select_related('plat', 'menu').order_by('-created_at')[:5]

    # Ajouter des propriétés pour les commandes
    for commande in commandes_recentes:
        if commande.statut == 'en_attente':
            commande.couleur_statut = 'yellow'
            commande.icone_statut = 'clock'
        elif commande.statut == 'confirmee':
            commande.couleur_statut = 'blue'
            commande.icone_statut = 'check-circle'
        elif commande.statut == 'prete':
            commande.couleur_statut = 'green'
            commande.icone_statut = 'utensils'
        elif commande.statut == 'livree':
            commande.couleur_statut = 'emerald'
            commande.icone_statut = 'truck'
        else:  # annulee
            commande.couleur_statut = 'red'
            commande.icone_statut = 'times-circle'
        
        # Vérifier si avis donné
        commande.avis_donne = Avis.objects.filter(
            utilisateur=request.user,
            commande=commande
        ).exists()

    # Statistiques personnelles
    total_commandes_mois = Commande.objects.filter(
        utilisateur=request.user,
        created_at__month=datetime.now().month,
        is_deleted=False
    ).count()

    avis_perso = Avis.objects.filter(
        utilisateur=request.user,
        is_deleted=False
    )
    moyenne_avis = avis_perso.aggregate(avg=Avg('note'))['avg'] or 0
    nombre_avis = avis_perso.count()

    # Plats favoris (top 3 par nombre de commandes)
    plats_favoris = Commande.objects.filter(
        utilisateur=request.user,
        is_deleted=False
    ).values('plat__nom').annotate(
        count=Count('plat')
    ).order_by('-count')[:3]

    context = {
        'menus_semaine': menus_par_jour,
        'commandes_recentes': commandes_recentes,
        'stats': {
            'commandes_mois': total_commandes_mois,
            'moyenne_avis': round(moyenne_avis, 1),
            'nombre_avis': nombre_avis,
            'plats_favoris': list(plats_favoris),
        },
        'semaine_debut': start_of_week,
        'semaine_fin': end_of_week,
    }
    return render(request, 'utilisateurs/dashboards/collaborateur_dashboard.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')
@login_required
def admin_menus(request):
    if request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')

    from Menus.models import Menu
    from django.core.paginator import Paginator

    # Récupérer tous les menus avec pagination
    menus = Menu.objects.select_related().order_by('-date')

    # Recherche et filtres
    search_query = request.GET.get('search', '')
    site_filter = request.GET.get('site', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        menus = menus.filter(titre__icontains=search_query)

    if site_filter:
        menus = menus.filter(site=site_filter)

    if status_filter:
        if status_filter == 'published':
            menus = menus.filter(est_publie=True)
        elif status_filter == 'draft':
            menus = menus.filter(est_publie=False)

    # Pagination
    paginator = Paginator(menus, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'site_filter': site_filter,
        'status_filter': status_filter,
    }
    return render(request, 'menus/admin/gerer_menus_semaine.html', context)
@login_required
def admin_users(request):
    if request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')
    
    search_form = UserSearchForm(request.GET or None)
    utilisateurs = Utilisateur.objects.all().order_by('nom')
    
    if search_form.is_valid():
        search_data = search_form.cleaned_data
        
        if search_data['search']:
            utilisateurs = utilisateurs.filter(
                Q(nom__icontains=search_data['search']) |
                Q(prenom__icontains=search_data['search']) |
                Q(email__icontains=search_data['search'])
            )
        
        if search_data['role']:
            utilisateurs = utilisateurs.filter(role=search_data['role'])
        
        if search_data['site']:
            utilisateurs = utilisateurs.filter(site=search_data['site'])
        
        if search_data['departement']:
            utilisateurs = utilisateurs.filter(departement=search_data['departement'])
    
    # Pagination
    paginator = Paginator(utilisateurs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
    }
    return render(request, 'utilisateurs/admin/users.html', context)

@login_required
def create_user(request):
    if request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Utilisateur {user.prenom} {user.nom} créé avec succès.')
            return redirect('admin_users')
    else:
        form = CustomUserCreationForm()
    
    context = {'form': form}
    return render(request, 'utilisateurs/admin/create_user.html', context)

@login_required
def update_user(request, user_id):
    if request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')
    
    user = get_object_or_404(Utilisateur, id=user_id)
    
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Utilisateur {user.prenom} {user.nom} mis à jour avec succès.')
            return redirect('admin_users')
    else:
        form = AdminUserUpdateForm(instance=user)
    
    context = {'form': form, 'user': user}
    return render(request, 'utilisateurs/admin/update_user.html', context)

@login_required
def delete_user(request, user_id):
    if request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')
    
    user = get_object_or_404(Utilisateur, id=user_id)
    
    if request.user.id == user.id:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('admin_users')
    
    if request.method == 'POST':
        user.is_deleted = True
        user.deleted_at = timezone.now()
        user.deleted_by = request.user.id
        user.save()
        messages.success(request, f'Utilisateur {user.prenom} {user.nom} supprimé avec succès.')
        return redirect('admin_users')
    
    context = {'user': user}
    return render(request, 'utilisateurs/admin/delete_user.html', context)
@login_required
def admin_orders(request):
    if request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')

    from Commandes.models import Commande
    from django.core.paginator import Paginator

    # Récupérer toutes les commandes avec pagination
    commandes = Commande.objects.select_related(
        'utilisateur', 'menu', 'plat'
    ).filter(is_deleted=False).order_by('-created_at')

    # Recherche et filtres
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    site_filter = request.GET.get('site', '')
    date_filter = request.GET.get('date', '')

    if search_query:
        commandes = commandes.filter(
            Q(utilisateur__nom__icontains=search_query) |
            Q(utilisateur__prenom__icontains=search_query) |
            Q(plat__nom__icontains=search_query)
        )

    if status_filter:
        commandes = commandes.filter(statut=status_filter)

    if site_filter:
        commandes = commandes.filter(utilisateur__site=site_filter)

    if date_filter:
        commandes = commandes.filter(created_at__date=date_filter)

    # Statistiques
    total_commandes = commandes.count()
    commandes_en_attente = commandes.filter(statut='en_attente').count()
    commandes_confirmees = commandes.filter(statut='confirmee').count()
    commandes_annulees = commandes.filter(statut='annulee').count()

    # Pagination
    paginator = Paginator(commandes, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'site_filter': site_filter,
        'date_filter': date_filter,
        'stats': {
            'total': total_commandes,
            'en_attente': commandes_en_attente,
            'confirmees': commandes_confirmees,
            'annulees': commandes_annulees,
        }
    }
    return render(request, 'commandes/admin/gestion_commandes.html', context)
@login_required
def admin_reports(request):
    if request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')

    from datetime import datetime, timedelta
    from django.db.models import Count, Avg, Sum
    from Commandes.models import Commande
    from Avis.models import Avis
    from Menus.models import Menu
    from Plats.models import Plat

    # Période d'analyse (dernier mois par défaut)
    periode = request.GET.get('periode', 'month')
    today = timezone.now().date()

    if periode == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif periode == 'month':
        start_date = today.replace(day=1)
        end_date = today
    else:  # year
        start_date = today.replace(month=1, day=1)
        end_date = today

    # Statistiques générales
    total_commandes = Commande.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        is_deleted=False
    ).count()

    total_utilisateurs = Commande.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        is_deleted=False
    ).values('utilisateur').distinct().count()

    # Répartition par statut
    commandes_par_statut = Commande.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        is_deleted=False
    ).values('statut').annotate(count=Count('id')).order_by('-count')

    # Top plats
    top_plats = Commande.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        is_deleted=False
    ).values('plat__nom').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    # Évolution journalière (derniers 7 jours)
    evolution_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        count = Commande.objects.filter(
            created_at__date=date,
            is_deleted=False
        ).count()
        evolution_data.append({
            'date': date.strftime('%d/%m'),
            'count': count
        })

    # Avis et satisfaction
    avis_stats = Avis.objects.filter(
        date_creation__date__gte=start_date,
        date_creation__date__lte=end_date
    ).aggregate(
        avg_note=Avg('note'),
        total_avis=Count('id')
    )

    # Répartition par site
    commandes_par_site = Commande.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        is_deleted=False
    ).values('utilisateur__site').annotate(count=Count('id')).order_by('-count')

    context = {
        'periode': periode,
        'start_date': start_date,
        'end_date': end_date,
        'stats': {
            'total_commandes': total_commandes,
            'total_utilisateurs': total_utilisateurs,
            'moyenne_commandes_par_utilisateur': round(total_commandes / total_utilisateurs, 1) if total_utilisateurs > 0 else 0,
            'avis_moyen': round(avis_stats['avg_note'] or 0, 1),
            'total_avis': avis_stats['total_avis'],
        },
        'commandes_par_statut': commandes_par_statut,
        'top_plats': top_plats,
        'evolution_data': evolution_data,
        'commandes_par_site': commandes_par_site,
    }

    return render(request, 'utilisateurs/admin/reports.html', context)
@login_required
def admin_menus_create(request):
    if request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')

    from Menus.forms import MenuForm
    from Menus.models import Menu

    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            menu = form.save()
            messages.success(request, f'Menu "{menu.titre}" créé avec succès.')
            return redirect('admin_menus')
    else:
        form = MenuForm()

    context = {'form': form}
    return render(request, 'menus/admin/modifier_menu.html', context)
@login_required
def admin_notifications(request):
    if request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')

    # Pour l'instant, une vue basique - à étendre avec un vrai système de notifications
    notifications = [
        {
            'id': 1,
            'type': 'info',
            'titre': 'Nouveaux menus à publier',
            'message': '3 menus sont en attente de publication pour la semaine prochaine.',
            'date': timezone.now(),
            'lue': False,
        },
        {
            'id': 2,
            'type': 'warning',
            'titre': 'Stock faible',
            'message': 'Le plat "Salade César" a un stock limité.',
            'date': timezone.now() - timedelta(hours=2),
            'lue': True,
        },
        {
            'id': 3,
            'type': 'success',
            'titre': 'Objectif atteint',
            'message': 'Taux de participation de 85% atteint cette semaine.',
            'date': timezone.now() - timedelta(days=1),
            'lue': True,
        },
    ]

    context = {
        'notifications': notifications,
        'total_notifications': len([n for n in notifications if not n['lue']]),
    }
    return render(request, 'utilisateurs/admin/notifications.html', context)

@login_required
def admin_reviews(request):
    if request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')

    from Avis.models import Avis
    from django.core.paginator import Paginator

    # Récupérer tous les avis avec pagination
    avis = Avis.objects.select_related(
        'utilisateur', 'commande__plat', 'commande__menu'
    ).order_by('-date_creation')

    # Recherche et filtres
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    rating_filter = request.GET.get('rating', '')

    if search_query:
        avis = avis.filter(
            Q(utilisateur__nom__icontains=search_query) |
            Q(utilisateur__prenom__icontains=search_query) |
            Q(commande__plat__nom__icontains=search_query)
        )

    if status_filter:
        if status_filter == 'pending':
            avis = avis.filter(approuve=False)
        elif status_filter == 'approved':
            avis = avis.filter(approuve=True)

    if rating_filter:
        avis = avis.filter(note=rating_filter)

    # Statistiques
    total_avis = avis.count()
    avis_approuves = avis.filter(approuve=True).count()
    avis_en_attente = avis.filter(approuve=False).count()
    moyenne_notes = avis.aggregate(avg=Avg('note'))['avg'] or 0

    # Pagination
    paginator = Paginator(avis, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'rating_filter': rating_filter,
        'stats': {
            'total': total_avis,
            'approuves': avis_approuves,
            'en_attente': avis_en_attente,
            'moyenne': round(moyenne_notes, 1),
        }
    }
    return render(request, 'avis/admin/moderation.html', context)
@login_required
def profile_view(request):
    return render(request, 'utilisateurs/profile.html')

@login_required
def toggle_theme_view(request):
    if request.method == 'POST':
        user = request.user
        user.theme_sombre = not user.theme_sombre
        user.save()
    return redirect(reverse(request.user.get_dashboard_url()))

@login_required
def menus_semaine_view(request):
    from datetime import datetime, timedelta
    from Menus.models import Menu
    from Commandes.models import Commande

    # Obtenir la semaine actuelle (lundi à dimanche)
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Lundi
    end_of_week = start_of_week + timedelta(days=6)  # Dimanche

    # Récupérer les menus de la semaine pour le site de l'utilisateur
    menus_semaine = Menu.objects.filter(
        date__gte=start_of_week,
        date__lte=end_of_week,
        site=request.user.site,
        est_publie=True
    ).order_by('date', 'jour')

    # Grouper par jour
    menus_par_jour = {}
    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi']

    for jour in jours:
        menus_jour = menus_semaine.filter(jour=jour)
        if menus_jour.exists():
            menu = menus_jour.first()
            # Vérifier si l'utilisateur a déjà commandé pour ce menu
            commande_existante = Commande.objects.filter(
                utilisateur=request.user,
                menu=menu,
                is_deleted=False
            ).exists()
            menus_par_jour[jour] = {
                'menu': menu,
                'commande_existante': commande_existante
            }

    context = {
        'menus_par_jour': menus_par_jour,
        'semaine_debut': start_of_week,
        'semaine_fin': end_of_week,
    }
    return render(request, "menus/menus_semaine.html", context)

@login_required
def historique_commandes_view(request):
    # Rediriger vers la vue mes_commandes dans l'app Commandes
    from django.shortcuts import redirect
    return redirect('commandes:mes_commandes')

@login_required
def donner_avis(request):
    return render(request, 'avis/donner_avis.html')

@login_required
def mes_avis_view(request):
    return render(request, 'avis/mes_avis.html')




class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'utilisateurs/password_reset.html'
    email_template_name = 'utilisateurs/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'utilisateurs/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'utilisateurs/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'utilisateurs/password_reset_complete.html'
