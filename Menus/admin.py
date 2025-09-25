from django.contrib import admin
from .models import Menu, MenuPlat

class MenuPlatInline(admin.TabularInline):
    model = MenuPlat
    extra = 1

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('date', 'jour', 'site', 'est_publie', 'date_limite_commande')
    list_filter = ('site', 'est_publie', 'date')
    search_fields = ('jour', 'site')
    inlines = [MenuPlatInline]
    list_editable = ('est_publie',)

@admin.register(MenuPlat)
class MenuPlatAdmin(admin.ModelAdmin):
    list_display = ('menu', 'plat', 'quantite_prevue', 'quantite_commandee')
    list_filter = ('menu__site', 'menu__date')