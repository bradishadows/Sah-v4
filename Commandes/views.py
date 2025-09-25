from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import Commande
from Menus.models import Menu
from Plats.models import Plat

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


@login_required
def mes_commandes(request):
    
    commandes = Commande.objects.filter(
        utilisateur=request.user,
        is_deleted=False
    ).select_related('menu', 'plat').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(commandes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'commandes_en_attente': commandes.filter(statut='en_attente').count(),
        'commandes_confirmees': commandes.filter(statut='confirmee').count(),
    }
    return render(request, 'commandes/collaborateur/mes_commandes.html', context)

@login_required
def commander_plat(request, menu_id):
    
    menu = get_object_or_404(Menu, id=menu_id, est_publie=True)
    
    # Vérifier si la commande est encore possible
    if timezone.now() > menu.date_limite_commande:
        messages.error(request, "La période de commande pour ce menu est terminée.")
        return redirect('menus_semaine')

    commande_existante = Commande.objects.filter(
        utilisateur=request.user,
        menu=menu,
        is_deleted=False
    ).first()
    
    if commande_existante:
        messages.warning(request, "Vous avez déjà commandé pour ce menu.")
        return redirect('menus_semaine')
    
    plats_disponibles = menu.menuplat_set.filter(plat__est_actif=True).select_related('plat')
    
    if request.method == 'POST':
        plat_id = request.POST.get('plat_id')
        notes_speciales = request.POST.get('notes_speciales', '')
        
        if plat_id:
            plat = get_object_or_404(Plat, id=plat_id, est_actif=True)
            
        
            commande = Commande.objects.create(
                utilisateur=request.user,
                menu=menu,
                plat=plat,
                notes_speciales=notes_speciales,
                statut='en_attente',
                created_by=request.user.id
            )
            
            # Mettre à jour le compteur de commandes dans MenuPlat
            menu_plat = menu.menuplat_set.filter(plat=plat).first()
            if menu_plat:
                menu_plat.quantite_commandee += 1
                menu_plat.save()
            
            messages.success(request, f"Votre commande pour {plat.nom} a été enregistrée avec succès.")
            return redirect('mes_commandes')
    
    context = {
        'menu': menu,
        'plats_disponibles': plats_disponibles,
        'commande_existante': commande_existante
    }
    return render(request, 'commandes/collaborateur/commander_plat.html', context)

@login_required
def modifier_commande(request, commande_id):
    """Modifier une commande existante"""
    commande = get_object_or_404(Commande, id=commande_id, utilisateur=request.user)
    
    # Vérifier si la modification est possible
    if timezone.now() > commande.menu.date_limite_commande:
        messages.error(request, "Impossible de modifier cette commande, la période est terminée.")
        return redirect('mes_commandes')
    
    if commande.statut not in ['en_attente', 'confirmee']:
        messages.error(request, "Impossible de modifier cette commande, son statut ne le permet pas.")
        return redirect('mes_commandes')
    
    plats_disponibles = commande.menu.menuplat_set.filter(plat__est_actif=True).select_related('plat')
    
    if request.method == 'POST':
        plat_id = request.POST.get('plat_id')
        notes_speciales = request.POST.get('notes_speciales', '')
        
        if plat_id:
            nouveau_plat = get_object_or_404(Plat, id=plat_id, est_actif=True)
            
            # Mettre à jour les compteurs de commandes
            if commande.plat != nouveau_plat:
                # Décrémenter l'ancien plat
                ancien_menu_plat = commande.menu.menuplat_set.filter(plat=commande.plat).first()
                if ancien_menu_plat:
                    ancien_menu_plat.quantite_commandee -= 1
                    ancien_menu_plat.save()
                
                # Incrémenter le nouveau plat
                nouveau_menu_plat = commande.menu.menuplat_set.filter(plat=nouveau_plat).first()
                if nouveau_menu_plat:
                    nouveau_menu_plat.quantite_commandee += 1
                    nouveau_menu_plat.save()
            
            # Mettre à jour la commande
            commande.plat = nouveau_plat
            commande.notes_speciales = notes_speciales
            commande.is_updated = True
            commande.updated_by = request.user.id
            commande.save()
            
            messages.success(request, "Votre commande a été modifiée avec succès.")
            return redirect('mes_commandes')
    
    context = {
        'commande': commande,
        'plats_disponibles': plats_disponibles
    }
    return render(request, 'commandes/collaborateur/modifier_commande.html', context)

@login_required
def annuler_commande(request, commande_id):
    """Annuler une commande"""
    commande = get_object_or_404(Commande, id=commande_id, utilisateur=request.user)
    
    # Vérifier si l'annulation est possible
    if timezone.now() > commande.menu.date_limite_commande:
        messages.error(request, "Impossible d'annuler cette commande, la période est terminée.")
        return redirect('mes_commandes')
    
    if request.method == 'POST':
        # Décrémenter le compteur de commandes
        menu_plat = commande.menu.menuplat_set.filter(plat=commande.plat).first()
        if menu_plat:
            menu_plat.quantite_commandee -= 1
            menu_plat.save()
        
        # Marquer la commande comme annulée
        commande.statut = 'annulee'
        commande.is_deleted = True
        commande.deleted_at = timezone.now()
        commande.deleted_by = request.user.id
        commande.save()
        
        messages.success(request, "Votre commande a été annulée avec succès.")
        return redirect('mes_commandes')
    
    context = {'commande': commande}
    return render(request, 'commandes/collaborateur/annuler_commande.html', context)

# === VUES ADMINISTRATEUR ===

@login_required
@user_passes_test(is_admin)
def gestion_commandes_admin(request):
    """Gestion des commandes pour l'administration"""
    statut = request.GET.get('statut', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    site = request.GET.get('site', '')
    
    commandes = Commande.objects.filter(is_deleted=False).select_related(
        'utilisateur', 'menu', 'plat'
    )
    
    # Filtres
    if statut:
        commandes = commandes.filter(statut=statut)
    
    if date_debut:
        commandes = commandes.filter(created_at__date__gte=date_debut)
    
    if date_fin:
        commandes = commandes.filter(created_at__date__lte=date_fin)
    
    if site:
        commandes = commandes.filter(menu__site=site)
    
    # Statistiques
    stats_commandes = commandes.aggregate(
        total=Count('id'),
        en_attente=Count('id', filter=Q(statut='en_attente')),
        confirmees=Count('id', filter=Q(statut='confirmee')),
        pretes=Count('id', filter=Q(statut='prete')),
        livrees=Count('id', filter=Q(statut='livree'))
    )
    
    # Pagination
    paginator = Paginator(commandes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'stats_commandes': stats_commandes,
        'statut_selected': statut,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'site_selected': site,
        'sites': ['Danga', 'Campus']
    }
    return render(request, 'commandes/admin/gestion_commandes.html', context)

@login_required
@user_passes_test(is_admin)
def modifier_statut_commande(request, commande_id):
    """Modifier le statut d'une commande (admin)"""
    commande = get_object_or_404(Commande, id=commande_id)
    
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        
        if nouveau_statut in dict(Commande.STATUT_CHOICES):
            ancien_statut = commande.statut
            commande.statut = nouveau_statut
            commande.is_updated = True
            commande.updated_by = request.user.id
            commande.save()
            
            messages.success(request, f"Statut de la commande #{commande.id} modifié de '{ancien_statut}' à '{nouveau_statut}'.")
        
        return redirect('gestion_commandes_admin')
    
    context = {
        'commande': commande,
        'statuts_choices': Commande.STATUT_CHOICES
    }
    return render(request, 'commandes/admin/modifier_statut.html', context)

# === VUES PRESTATAIRE ===

@login_required
@user_passes_test(is_prestataire)
def commandes_prestataire(request):
    """Vue des commandes pour le prestataire"""
    date_cible = request.GET.get('date', timezone.now().date())
    site = request.GET.get('site', 'Danga')
    
    commandes = Commande.objects.filter(
        menu__date=date_cible,
        menu__site=site,
        statut__in=['confirmee', 'prete'],
        is_deleted=False
    ).select_related('utilisateur', 'menu', 'plat').order_by('plat__nom')
    
    # Consolidation par plat
    consolidation_plats = {}
    for commande in commandes:
        plat_nom = commande.plat.nom
        if plat_nom not in consolidation_plats:
            consolidation_plats[plat_nom] = {
                'plat': commande.plat,
                'quantite': 0,
                'commandes': [],
                'notes_speciales': []
            }
        
        consolidation_plats[plat_nom]['quantite'] += 1
        consolidation_plats[plat_nom]['commandes'].append(commande)
        if commande.notes_speciales:
            consolidation_plats[plat_nom]['notes_speciales'].append(commande.notes_speciales)
    
    # Préparation pour livraison
    if request.method == 'POST':
        commande_id = request.POST.get('commande_id')
        action = request.POST.get('action')
        
        if commande_id and action:
            commande = get_object_or_404(Commande, id=commande_id)
            if action == 'prete':
                commande.statut = 'prete'
                commande.save()
            elif action == 'livree':
                commande.statut = 'livree'
                commande.save()
    
    context = {
        'commandes': commandes,
        'consolidation_plats': consolidation_plats,
        'date_cible': date_cible,
        'site_selected': site,
        'sites': ['Danga', 'Campus'],
        'total_commandes': commandes.count()
    }
    return render(request, 'commandes/prestataire/commandes_jour.html', context)

@login_required
@user_passes_test(is_prestataire)
def preparation_commandes(request):
    """Interface de préparation des commandes"""
    aujourdhui = timezone.now().date()
    sites = ['Danga', 'Campus']
    
    preparation_data = {}
    for site in sites:
        commandes_site = Commande.objects.filter(
            menu__date=aujourdhui,
            menu__site=site,
            statut__in=['confirmee', 'prete'],
            is_deleted=False
        ).select_related('plat')
        
        # Regroupement par plat
        plats_quantites = {}
        for commande in commandes_site:
            plat_key = f"{commande.plat.nom}"
            if plat_key not in plats_quantites:
                plats_quantites[plat_key] = {
                    'plat': commande.plat,
                    'quantite': 0,
                    'statut_prete': 0,
                    'statut_confirmee': 0
                }
            
            plats_quantites[plat_key]['quantite'] += 1
            if commande.statut == 'prete':
                plats_quantites[plat_key]['statut_prete'] += 1
            else:
                plats_quantites[plat_key]['statut_confirmee'] += 1
        
        preparation_data[site] = {
            'plats_quantites': plats_quantites,
            'total_commandes': commandes_site.count()
        }
    
    context = {
        'preparation_data': preparation_data,
        'aujourdhui': aujourdhui
    }
    return render(request, 'commandes/prestataire/preparation.html', context)

# === API POUR STATISTIQUES ===

@login_required
@user_passes_test(is_admin)
def api_statistiques_commandes(request):
    """API pour les statistiques des commandes"""
    date_debut = request.GET.get('date_debut', (timezone.now() - timedelta(days=30)).date())
    date_fin = request.GET.get('date_fin', timezone.now().date())
    
    commandes = Commande.objects.filter(
        created_at__date__range=[date_debut, date_fin],
        is_deleted=False
    )
    
    # Statistiques par jour
    stats_par_jour = commandes.extra(
        {'date': "DATE(created_at)"}
    ).values('date').annotate(
        total=Count('id'),
        confirmees=Count('id', filter=Q(statut='confirmee')),
        livrees=Count('id', filter=Q(statut='livree'))
    ).order_by('date')
    
    # Statistiques par plat
    stats_par_plat = commandes.values('plat__nom').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    return JsonResponse({
        'stats_par_jour': list(stats_par_jour),
        'stats_par_plat': list(stats_par_plat),
        'periode': {'debut': date_debut, 'fin': date_fin}
    })