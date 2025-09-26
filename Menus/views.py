from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import Menu, MenuPlat
from .forms import MenuForm, MenuPlatFormSet
from Plats.models import Plat

# === FONCTIONS UTILITAIRES ===

def is_admin(user):
    """Vérifie si l'utilisateur est un administrateur"""
    return user.is_authenticated and user.role == 'admin'

def is_prestataire(user):
    """Vérifie si l'utilisateur est un prestataire"""
    return user.is_authenticated and user.role == 'prestataire'

def get_semaine_courante():
    """Retourne les dates de la semaine courante (lundi à vendredi)"""
    today = timezone.now().date()
    start_week = today - timedelta(days=today.weekday())  # Lundi
    return [start_week + timedelta(days=i) for i in range(5)]  # Lundi à Vendredi

# === VUES ADMINISTRATEUR ===

@login_required
@user_passes_test(is_admin)
def dashboard_admin(request):
    """Tableau de bord administrateur"""
    date_debut_semaine = get_semaine_courante()[0]
    date_fin_semaine = get_semaine_courante()[4]
    
    menus_semaine = Menu.objects.filter(
        date__range=[date_debut_semaine, date_fin_semaine]
    )
    
    total_commandes = MenuPlat.objects.filter(
        menu__in=menus_semaine
    ).aggregate(total=Sum('quantite_commandee'))['total'] or 0
    
    taux_participation = 0  
    
    context = {
        'menus_semaine': menus_semaine,
        'total_commandes': total_commandes,
        'taux_participation': taux_participation,
        'menus_publies': menus_semaine.filter(est_publie=True).count(),
        'menus_non_publies': menus_semaine.filter(est_publie=False).count(),
    }
    return render(request, 'menus/admin/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def gerer_menus_semaine(request):
    """Gestion des menus de la semaine"""
    dates_semaine = get_semaine_courante()
    sites = ['Danga', 'Campus']
    for date_obj in dates_semaine:
        for site in sites:
            Menu.objects.get_or_create(
                date=date_obj,
                site=site,
                defaults={
                    'jour': date_obj.strftime('%A').lower(),
                    'date_limite_commande': timezone.make_aware(
                        datetime.combine(date_obj, datetime.min.time())
                    ) + timedelta(hours=12) 
                }
            )
    
    menus_semaine = Menu.objects.filter(date__in=dates_semaine)
    
    if request.method == 'POST':
        # Gestion de la publication des menus
        menu_id = request.POST.get('menu_id')
        action = request.POST.get('action')
        
        if menu_id and action:
            menu = get_object_or_404(Menu, id=menu_id)
            if action == 'publier':
                menu.est_publie = True
                menu.save()
                messages.success(request, f"Menu du {menu.date} ({menu.site}) publié avec succès.")
            elif action == 'depublier':
                menu.est_publie = False
                menu.save()
                messages.success(request, f"Menu du {menu.date} ({menu.site}) dépublié.")
    
    context = {
        'menus_semaine': menus_semaine,
        'dates_semaine': dates_semaine,
        'sites': sites
    }
    return render(request, 'menus/admin/gerer_menus_semaine.html', context)

@login_required
@user_passes_test(is_admin)
def modifier_menu(request, menu_id):
    """Modification d'un menu spécifique"""
    menu = get_object_or_404(Menu, id=menu_id)
    plats_disponibles = Plat.objects.filter(est_actif=True, is_deleted=False)
    
    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu)
        formset = MenuPlatFormSet(request.POST, instance=menu)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f"Menu du {menu.date} ({menu.site}) modifié avec succès.")
            return redirect('gerer_menus_semaine')
    else:
        form = MenuForm(instance=menu)
        formset = MenuPlatFormSet(instance=menu)
    
    context = {
        'menu': menu,
        'form': form,
        'formset': formset,
        'plats_disponibles': plats_disponibles
    }
    return render(request, 'menus/admin/modifier_menu.html', context)

@login_required
@user_passes_test(is_admin)
def suivi_commandes(request):
    """Suivi des commandes pour la semaine en cours"""
    dates_semaine = get_semaine_courante()
    menus_semaine = Menu.objects.filter(date__in=dates_semaine)
   
    commandes_par_site_jour = {}
    for menu in menus_semaine:
        key = f"{menu.site}_{menu.jour}"
        plats_commandes = MenuPlat.objects.filter(menu=menu).select_related('plat')
        commandes_par_site_jour[key] = {
            'menu': menu,
            'plats': plats_commandes,
            'total_commandes': plats_commandes.aggregate(total=Sum('quantite_commandee'))['total'] or 0
        }
    
    context = {
        'commandes_par_site_jour': commandes_par_site_jour,
        'dates_semaine': dates_semaine
    }
    return render(request, 'menus/admin/suivi_commandes.html', context)



@login_required
@user_passes_test(is_prestataire)
def dashboard_prestataire(request):
    """Tableau de bord prestataire"""

    dates_semaine = get_semaine_courante()
    menus_semaine = Menu.objects.filter(date__in=dates_semaine)

    consolidation_site = {}
    for site in ['Danga', 'Campus']:
        menus_site = menus_semaine.filter(site=site)
        total_commandes = MenuPlat.objects.filter(
            menu__in=menus_site
        ).aggregate(total=Sum('quantite_commandee'))['total'] or 0
        
        consolidation_site[site] = {
            'menus': menus_site,
            'total_commandes': total_commandes,
            'details_par_jour': {}
        }
        
        for menu in menus_site:
            plats_menu = MenuPlat.objects.filter(menu=menu).select_related('plat')
            consolidation_site[site]['details_par_jour'][menu.jour] = plats_menu
    
    context = {
        'consolidation_site': consolidation_site,
        'dates_semaine': dates_semaine
    }
    return render(request, 'menus/prestataire/dashboard.html', context)

@login_required
@user_passes_test(is_prestataire)
def consolidation_commandes(request):
    date_debut = request.GET.get('date_debut', get_semaine_courante()[0])
    date_fin = request.GET.get('date_fin', get_semaine_courante()[4])
    site = request.GET.get('site', 'Danga')

    menus = Menu.objects.filter(
        date__range=[date_debut, date_fin],
        site=site
    )

    consolidation = []
    for menu in menus:
        plats = MenuPlat.objects.filter(menu=menu).select_related('plat')
        consolidation.append({
            'menu': menu,
            'plats': plats,
            'total_commandes': plats.aggregate(total=Sum('quantite_commandee'))['total'] or 0
        })

    context = {
        'consolidation': consolidation,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'site_selected': site,
        'sites': ['Danga', 'Campus']
    }
    return render(request, 'menus/prestataire/consolidation.html', context)

@login_required
@user_passes_test(is_prestataire)
def prestataire_gerer_menus_semaine(request):
    """Gestion des menus de la semaine pour prestataire"""
    dates_semaine = get_semaine_courante()
    sites = ['Danga', 'Campus']

    # Créer les menus squelettes s'ils n'existent pas
    for date_obj in dates_semaine:
        for site in sites:
            Menu.objects.get_or_create(
                date=date_obj,
                site=site,
                defaults={
                    'jour': date_obj.strftime('%A').lower(),
                    'date_limite_commande': timezone.make_aware(
                        datetime.combine(date_obj, datetime.min.time())
                    ) + timedelta(hours=12),
                    'created_by': request.user.id
                }
            )

    menus_semaine = Menu.objects.filter(date__in=dates_semaine)

    if request.method == 'POST':
        # Gestion de la publication des menus
        menu_id = request.POST.get('menu_id')
        action = request.POST.get('action')

        if menu_id and action:
            menu = get_object_or_404(Menu, id=menu_id)
            if action == 'publier':
                menu.est_publie = True
                menu.updated_by = request.user.id
                menu.save()
                messages.success(request, f"Menu du {menu.date} ({menu.site}) publié avec succès.")
            elif action == 'depublier':
                menu.est_publie = False
                menu.updated_by = request.user.id
                menu.save()
                messages.success(request, f"Menu du {menu.date} ({menu.site}) dépublié.")

    context = {
        'menus_semaine': menus_semaine,
        'dates_semaine': dates_semaine,
        'sites': sites
    }
    return render(request, 'menus/prestataire/gerer_menus_semaine.html', context)

@login_required
@user_passes_test(is_prestataire)
def create_or_edit_menu_prestataire(request, menu_id=None):
    """Créer ou modifier un menu pour prestataire"""
    if menu_id:
        menu = get_object_or_404(Menu, id=menu_id)
        is_editing = True
    else:
        menu = None
        is_editing = False

    plats_disponibles = Plat.objects.filter(est_actif=True, is_deleted=False)

    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu)
        formset = MenuPlatFormSet(request.POST, instance=menu)

        if form.is_valid() and formset.is_valid():
            menu_instance = form.save(commit=False)
            if not is_editing:
                menu_instance.created_by = request.user.id
            else:
                menu_instance.updated_by = request.user.id
            menu_instance.save()

            formset.save()
            messages.success(request, f"Menu {'modifié' if is_editing else 'créé'} avec succès.")
            return redirect('prestataire_gerer_menus_semaine')
    else:
        form = MenuForm(instance=menu)
        formset = MenuPlatFormSet(instance=menu)

    context = {
        'menu': menu,
        'form': form,
        'formset': formset,
        'plats_disponibles': plats_disponibles,
        'is_editing': is_editing
    }
    return render(request, 'menus/prestataire/create_menu.html', context)



@login_required
def menus_semaine(request):
 
    dates_semaine = get_semaine_courante()
    menus_semaine = Menu.objects.filter(
        date__in=dates_semaine,
        est_publie=True
    ).prefetch_related('menuplat_set__plat')
    

    maintenant = timezone.now()
    for menu in menus_semaine:
        menu.commandes_ouvertes = maintenant < menu.date_limite_commande
    
    context = {
        'menus_semaine': menus_semaine,
        'dates_semaine': dates_semaine,
        'aujourdhui': timezone.now().date()
    }
    return render(request, 'menus/collaborateur/menus_semaine.html', context)

@login_required
def commander_menu(request, menu_id):
    """Commander un plat pour un menu"""
    menu = get_object_or_404(Menu, id=menu_id, est_publie=True)

    if timezone.now() > menu.date_limite_commande:
        messages.error(request, "La période de commande pour ce menu est terminée.")
        return redirect('menus_semaine')
    
    plats_disponibles = menu.menuplat_set.all().select_related('plat')
    
    if request.method == 'POST':
        plat_id = request.POST.get('plat_id')
        if plat_id:

            menu_plat = get_object_or_404(MenuPlat, id=plat_id, menu=menu)
            menu_plat.quantite_commandee += 1
            menu_plat.save()
            
            messages.success(request, f"Votre commande pour {menu_plat.plat.nom} a été enregistrée.")
            return redirect('menus_semaine')
    
    context = {
        'menu': menu,
        'plats_disponibles': plats_disponibles
    }
    return render(request, 'menus/collaborateur/commander_menu.html', context)



@login_required
def api_menus_a_publicr(request):

    menus_a_publier = Menu.objects.filter(
        est_publie=False,
        date__gte=timezone.now().date()
    ).count()
    
    return JsonResponse({'menus_a_publier': menus_a_publier})

@login_required
def api_commandes_limite(request):
    menus_limite = Menu.objects.filter(
        est_publie=True,
        date_limite_commande__lte=timezone.now() + timedelta(hours=24),
        date_limite_commande__gte=timezone.now()
    ).count()
    
    return JsonResponse({'menus_limite': menus_limite})