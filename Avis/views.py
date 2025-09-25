from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from .models import Avis
from Plats.models import Plat
from Commandes.models import Commande



def is_admin(user):
 
    return user.is_authenticated and user.role == 'admin'

def has_commande_plat(utilisateur, plat):
   
    return Commande.objects.filter(
        utilisateur=utilisateur,
        plat=plat,
        statut__in=['confirmee', 'prete', 'livree'],
        is_deleted=False
    ).exists()

# === VUES COLLABORATEUR ===

@login_required
def mes_avis(request):

    avis = Avis.objects.filter(
        utilisateur=request.user,
        is_deleted=False
    ).select_related('plat').order_by('-created_at')

    stats_perso = avis.aggregate(
        total_avis=Count('id'),
        moyenne_perso=Avg('note'),
        avis_approuves=Count('id', filter=Q(est_approuve=True))
    )

    paginator = Paginator(avis, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'stats_perso': stats_perso,
    }
    return render(request, 'avis/collaborateur/mes_avis.html', context)

@login_required
def donner_avis(request, commande_id=None, plat_id=None):

    if commande_id:
        commande = get_object_or_404(Commande, id=commande_id, utilisateur=request.user)
        plat = commande.plat
    elif plat_id:
        plat = get_object_or_404(Plat, id=plat_id, est_actif=True)
        commande = None
    else:
        messages.error(request, "Plat ou commande non spécifié.")
        return redirect('menus_semaine')
   
    if not has_commande_plat(request.user, plat):
        messages.error(request, "Vous devez avoir commandé ce plat pour pouvoir donner un avis.")
        return redirect('menus_semaine')
    
   
    avis_existant = None
    if commande:
        avis_existant = Avis.objects.filter(utilisateur=request.user, commande=commande).first()
    
    if request.method == 'POST':
        note = request.POST.get('note')
        commentaire = request.POST.get('commentaire', '')
        est_anonyme = request.POST.get('est_anonyme') == 'on'
        
        if note:
            if avis_existant:
               
                avis_existant.note = note
                avis_existant.commentaire = commentaire
                avis_existant.est_anonyme = est_anonyme
                avis_existant.is_updated = True
                avis_existant.updated_by = request.user.id
                avis_existant.save()
                messages.success(request, "Votre avis a été modifié avec succès.")
            else:
                
                avis = Avis.objects.create(
                    utilisateur=request.user,
                    plat=plat,
                    commande=commande,
                    note=note,
                    commentaire=commentaire,
                    est_anonyme=est_anonyme,
                    created_by=request.user.id
                )
                messages.success(request, "Merci pour votre avis !")
            
            return redirect('mes_avis')
    
    context = {
        'plat': plat,
        'commande': commande,
        'avis_existant': avis_existant,
        'note_range': range(1, 6)
    }
    return render(request, 'avis/collaborateur/donner_avis.html', context)

@login_required
def modifier_avis(request, avis_id):

    avis = get_object_or_404(Avis, id=avis_id, utilisateur=request.user)
    
    if request.method == 'POST':
        note = request.POST.get('note')
        commentaire = request.POST.get('commentaire', '')
        est_anonyme = request.POST.get('est_anonyme') == 'on'
        
        if note:
            avis.note = note
            avis.commentaire = commentaire
            avis.est_anonyme = est_anonyme
            avis.is_updated = True
            avis.updated_by = request.user.id
            avis.save()
            
            messages.success(request, "Votre avis a été modifié avec succès.")
            return redirect('mes_avis')
    
    context = {
        'avis': avis,
        'note_range': range(1, 6)
    }
    return render(request, 'avis/collaborateur/modifier_avis.html', context)

@login_required
def supprimer_avis(request, avis_id):
 
    avis = get_object_or_404(Avis, id=avis_id, utilisateur=request.user)
    
    if request.method == 'POST':
        avis.is_deleted = True
        avis.deleted_at = timezone.now()
        avis.deleted_by = request.user.id
        avis.save()
        
        messages.success(request, "Votre avis a été supprimé.")
        return redirect('mes_avis')
    
    context = {'avis': avis}
    return render(request, 'avis/collaborateur/supprimer_avis.html', context)



@login_required
@user_passes_test(is_admin)
def moderation_avis(request):
    """Modération des avis pour l'administration"""
    statut = request.GET.get('statut', 'en_attente')  # en_attente, approuves, rejetes
    plat_id = request.GET.get('plat_id', '')
    
    avis = Avis.objects.filter(is_deleted=False).select_related('utilisateur', 'plat')
    

    if statut == 'en_attente':
        avis = avis.filter(est_approuve=False)
    elif statut == 'approuves':
        avis = avis.filter(est_approuve=True)
    
    if plat_id:
        avis = avis.filter(plat_id=plat_id)
    

    stats_avis = avis.aggregate(
        total=Count('id'),
        moyenne_generale=Avg('note'),
        avec_commentaire=Count('id', filter=~Q(commentaire='')),
        anonymes=Count('id', filter=Q(est_anonyme=True))
    )
    
 
    paginator = Paginator(avis, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    plats = Plat.objects.filter(est_actif=True)
    
    context = {
        'page_obj': page_obj,
        'stats_avis': stats_avis,
        'statut_selected': statut,
        'plat_selected': plat_id,
        'plats': plats
    }
    return render(request, 'avis/admin/moderation.html', context)

@login_required
@user_passes_test(is_admin)
def approuver_avis(request, avis_id):
  
    avis = get_object_or_404(Avis, id=avis_id)
    
    if request.method == 'POST':
        avis.est_approuve = True
        avis.is_updated = True
        avis.updated_by = request.user.id
        avis.save()
        
        messages.success(request, f"Avis #{avis.id} approuvé avec succès.")
        return redirect('moderation_avis')
    
    context = {'avis': avis}
    return render(request, 'avis/admin/approuver_avis.html', context)

@login_required
@user_passes_test(is_admin)
def rejeter_avis(request, avis_id):

    avis = get_object_or_404(Avis, id=avis_id)
    
    if request.method == 'POST':
        avis.is_deleted = True
        avis.deleted_at = timezone.now()
        avis.deleted_by = request.user.id
        avis.save()
        
        messages.success(request, f"Avis #{avis.id} rejeté et supprimé.")
        return redirect('moderation_avis')
    
    context = {'avis': avis}
    return render(request, 'avis/admin/rejeter_avis.html', context)

@login_required
@user_passes_test(is_admin)
def statistiques_avis(request):

    date_debut = request.GET.get('date_debut', (timezone.now() - timedelta(days=30)).date())
    date_fin = request.GET.get('date_fin', timezone.now().date())
    
    avis = Avis.objects.filter(
        created_at__date__range=[date_debut, date_fin],
        est_approuve=True,
        is_deleted=False
    )

    stats_generales = avis.aggregate(
        total_avis=Count('id'),
        moyenne_generale=Avg('note'),
        taux_reponse=Count('id')  
    )

    repartition_notes = {}
    for i in range(1, 6):
        repartition_notes[i] = avis.filter(note=i).count()

    top_plats = avis.values('plat__nom', 'plat_id').annotate(
        moyenne=Avg('note'),
        nb_avis=Count('id')
    ).order_by('-moyenne')[:10]
    
    avis_recents = avis.select_related('utilisateur', 'plat').order_by('-created_at')[:10]
    
    context = {
        'stats_generales': stats_generales,
        'repartition_notes': repartition_notes,
        'top_plats': top_plats,
        'avis_recents': avis_recents,
        'date_debut': date_debut,
        'date_fin': date_fin
    }
    return render(request, 'avis/admin/statistiques.html', context)



def avis_plats(request, plat_id=None):

    if plat_id:
        plat = get_object_or_404(Plat, id=plat_id, est_actif=True)
        avis = Avis.objects.filter(
            plat=plat,
            est_approuve=True,
            is_deleted=False
        ).select_related('utilisateur').order_by('-created_at')
        
        stats_plat = avis.aggregate(
            moyenne=Avg('note'),
            total=Count('id')
        )
    else:
        plat = None
        avis = Avis.objects.filter(
            est_approuve=True,
            is_deleted=False
        ).select_related('utilisateur', 'plat').order_by('-created_at')[:50]
        stats_plat = None
    
  
    paginator = Paginator(avis, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'plat': plat,
        'page_obj': page_obj,
        'stats_plat': stats_plat,
        'note_range': range(1, 6)
    }
    return render(request, 'avis/public/avis_plats.html', context)



@login_required
def api_avis_plat(request, plat_id):
    """API pour récupérer les avis d'un plat"""
    plat = get_object_or_404(Plat, id=plat_id)
    
    avis = Avis.objects.filter(
        plat=plat,
        est_approuve=True,
        is_deleted=False
    ).select_related('utilisateur').order_by('-created_at')[:10]
    
    data = {
        'plat': {
            'id': plat.id,
            'nom': plat.nom,
            'moyenne': Avis.objects.filter(
                plat=plat, 
                est_approuve=True
            ).aggregate(moyenne=Avg('note'))['moyenne'] or 0
        },
        'avis': []
    }
    
    for avis in avis:
        data['avis'].append({
            'utilisateur': avis.utilisateur.prenom if not avis.est_anonyme else 'Anonyme',
            'note': avis.note,
            'commentaire': avis.commentaire,
            'date': avis.created_at.strftime('%d/%m/%Y'),
            'anonyme': avis.est_anonyme
        })
    
    return JsonResponse(data)

@login_required
def api_demande_avis(request):
    """API pour vérifier les plats sans avis"""

    commandes_sans_avis = Commande.objects.filter(
        utilisateur=request.user,
        statut__in=['confirmee', 'prete', 'livree'],
        created_at__gte=timezone.now() - timedelta(days=7),
        is_deleted=False
    ).exclude(
        id__in=Avis.objects.filter(utilisateur=request.user).values('commande_id')
    ).select_related('plat')[:5]
    
    data = {
        'plats_sans_avis': [
            {
                'commande_id': cmd.id,
                'plat_id': cmd.plat.id,
                'plat_nom': cmd.plat.nom,
                'date_commande': cmd.created_at.strftime('%d/%m/%Y')
            }
            for cmd in commandes_sans_avis
        ],
        'total_sans_avis': commandes_sans_avis.count()
    }
    
    return JsonResponse(data)


@login_required
def notifications_avis(request):

    plats_sans_avis = Commande.objects.filter(
        utilisateur=request.user,
        created_at__gte=timezone.now() - timedelta(days=3),
        is_deleted=False
    ).exclude(
        id__in=Avis.objects.filter(utilisateur=request.user).values('commande_id')
    ).select_related('plat').distinct()[:5]
    
    context = {
        'plats_sans_avis': plats_sans_avis
    }
    return render(request, 'avis/collaborateur/notifications_avis.html', context)