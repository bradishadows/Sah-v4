from django.contrib import admin
from .models import CategoriePlat, Plat

@admin.register(CategoriePlat)
class CategoriePlatAdmin(admin.ModelAdmin):
    list_display = ('nom', 'couleur')
    search_fields = ('nom',)

@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'est_actif')
    list_filter = ('categorie', 'est_actif')
    search_fields = ('nom', 'description')
