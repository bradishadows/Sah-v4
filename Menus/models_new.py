from django.db import models
from django.utils import timezone
from datetime import date

class Menu(models.Model):
    JOURS_SEMAINE = [
        ('lundi', 'Lundi'),
        ('mardi', 'Mardi'),
        ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'),
        ('vendredi', 'Vendredi'),
    ]

    jour = models.CharField(max_length=10, choices=JOURS_SEMAINE)
    date = models.DateField()
    titre = models.CharField(max_length=200, blank=True, default='')
    description = models.TextField(blank=True, default='')
    plats = models.ManyToManyField('Plats.Plat', through='MenuPlat')
    site = models.CharField(max_length=100, choices=[('Danga', 'Danga'), ('Campus', 'Campus')])
    est_publie = models.BooleanField(default=False)

    # Limites de commande
    date_limite_commande = models.DateTimeField()
    max_commandes = models.IntegerField(default=100)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_updated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Menu {self.get_jour_display()} {self.date} - {self.site}"

    @property
    def est_disponible(self):
        return self.est_publie and timezone.now() < self.date_limite_commande

    class Meta:
        unique_together = ['date', 'site', 'jour']
        ordering = ['date', 'site']

class MenuPlat(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.SET_NULL, null=True, blank=True)
    plat = models.ForeignKey('Plats.Plat', on_delete=models.SET_NULL, null=True, blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantite_max = models.IntegerField(default=0)
    quantite_prevue = models.IntegerField(default=0)
    quantite_commandee = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.menu} - {self.plat}"
