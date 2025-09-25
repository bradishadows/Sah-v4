from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import CategoriePlat, Plat
from .forms import CategoriePlatForm, PlatForm



def is_admin(user):
    
    return user.is_authenticated and user.role == 'admin'

def is_prestataire(user):
    return user.is_authenticated and user.role == "prestataire"

def is_admin_or_prestataire(user):
    return is_admin(user) or is_prestataire(user)

@login_required
@user_passes_test(is_admin)
def liste_categories(request):

    categories = CategoriePlat.objects.filter(is_deleted=False)
    

    query = request.GET.get('q')
    if query:
        categories = categories.filter(Q(nom__icontains=query) | Q(description__icontains=query))
    
 
    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query
    }
    return render(request, 'menus/categories/liste.html', context)

@login_required
@user_passes_test(is_admin  )
def creer_categorie(request):

    if request.method == 'POST':
        form = CategoriePlatForm(request.POST)
        if form.is_valid():
            categorie = form.save(commit=False)
            categorie.created_by = request.user
            categorie.save()
            messages.success(request, f'La catégorie "{categorie.nom}" a été créée avec succès.')
            return redirect('liste_categories')
    else:
        form = CategoriePlatForm()
    
    context = {'form': form}
    return render(request, 'menus/categories/form.html', context)

@login_required
@user_passes_test(is_admin)
def modifier_categorie(request, pk):

    categorie = get_object_or_404(CategoriePlat, pk=pk)
    
    if request.method == 'POST':
        form = CategoriePlatForm(request.POST, instance=categorie)
        if form.is_valid():
            categorie = form.save(commit=False)
            categorie.is_updated = True
            categorie.updated_by = request.user.id
            categorie.save()
            messages.success(request, f'La catégorie "{categorie.nom}" a été modifiée avec succès.')
            return redirect('liste_categories')
    else:
        form = CategoriePlatForm(instance=categorie)
    
    context = {'form': form, 'categorie': categorie}
    return render(request, 'menus/categories/form.html', context)

@login_required
@user_passes_test(is_admin)
def supprimer_categorie(request, pk):

    categorie = get_object_or_404(CategoriePlat, pk=pk)
    
    if request.method == 'POST':
        categorie.is_deleted = True
        categorie.deleted_by = request.user.id
        categorie.save()
        messages.success(request, f'La catégorie "{categorie.nom}" a été supprimée avec succès.')
        return redirect('liste_categories')
    
    context = {'categorie': categorie}
    return render(request, 'menus/categories/supprimer.html', context)

@login_required
def liste_plats(request):
    plats = Plat.objects.filter(est_actif=True, is_deleted=False)

    categorie_id = request.GET.get('categorie')
    if categorie_id:
        plats = plats.filter(categorie_id=categorie_id)

    query = request.GET.get('q')
    if query:
        plats = plats.filter(Q(nom__icontains=query) | Q(description__icontains=query))

    paginator = Paginator(plats, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = CategoriePlat.objects.filter(is_deleted=False)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'categorie_selected': int(categorie_id) if categorie_id else None,
        'query': query
    }
    return render(request, 'menus/plats/liste.html', context)

@login_required
@user_passes_test(is_admin)
def creer_plat(request):

    if request.method == 'POST':
        form = PlatForm(request.POST, request.FILES)
        if form.is_valid():
            plat = form.save(commit=False)
            plat.created_by = request.user
            plat.save()
            messages.success(request, f'Le plat "{plat.nom}" a été créé avec succès.')
            return redirect('liste_plats')
    else:
        form = PlatForm()
    
    context = {'form': form}
    return render(request, 'menus/plats/form.html', context)

@login_required
@user_passes_test(is_admin)
def modifier_plat(request, pk):

    plat = get_object_or_404(Plat, pk=pk)
    
    if request.method == 'POST':
        form = PlatForm(request.POST, request.FILES, instance=plat)
        if form.is_valid():
            plat = form.save(commit=False)
            plat.is_updated = True
            plat.updated_by = request.user.id
            plat.save()
            messages.success(request, f'Le plat "{plat.nom}" a été modifié avec succès.')
            return redirect('liste_plats')
    else:
        form = PlatForm(instance=plat)
    
    context = {'form': form, 'plat': plat}
    return render(request, 'menus/plats/form.html', context)

@login_required
@user_passes_test(is_admin)
def supprimer_plat(request, pk):

    plat = get_object_or_404(Plat, pk=pk)
    
    if request.method == 'POST':
        plat.is_deleted = True
        plat.deleted_by = request.user.id
        plat.save()
        messages.success(request, f'Le plat "{plat.nom}" a été supprimé avec succès.')
        return redirect('liste_plats')
    
    context = {'plat': plat}
    return render(request, 'menus/plats/supprimer.html', context)

@login_required
@user_passes_test(is_admin)
def activer_desactiver_plat(request, pk):
    """Active ou désactive un plat"""
    plat = get_object_or_404(Plat, pk=pk)
    
    if plat.est_actif:
        plat.est_actif = False
        messages.success(request, f'Le plat "{plat.nom}" a été désactivé.')
    else:
        plat.est_actif = True
        messages.success(request, f'Le plat "{plat.nom}" a été activé.')
    
    plat.save()
    return redirect('liste_plats')

@login_required
def detail_plat(request, pk):

    plat = get_object_or_404(Plat, pk=pk, est_actif=True, is_deleted=False)
    
    context = {'plat': plat}
    return render(request, 'menus/plats/detail.html', context)
