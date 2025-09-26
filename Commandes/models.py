from django.db import models
from django.utils import timezone

class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('prete', 'Prête'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]
    
    utilisateur = models.ForeignKey('Utilisateurs.Utilisateur', on_delete=models.SET_NULL, null=True, blank=True)
    menu = models.ForeignKey('Menus.Menu', on_delete=models.SET_NULL, null=True, blank=True)
    plat = models.ForeignKey('Plats.Plat', on_delete=models.SET_NULL, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    notes_speciales = models.TextField(blank=True)
    
    # Horodatage
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_updated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"Commande #{self.id} - {self.utilisateur.prenom} {self.utilisateur.nom}"
    
    class Meta:
        unique_together = ['utilisateur', 'menu', 'plat']
        ordering = ['-created_at']
