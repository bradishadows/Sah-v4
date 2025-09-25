from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Avis(models.Model):
    utilisateur = models.ForeignKey('Utilisateurs.Utilisateur', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Utilisateur")
    plat = models.ForeignKey('Plats.Plat', on_delete=models.SET_NULL, null=True, blank=True)
    commande = models.ForeignKey('Commandes.Commande', on_delete=models.SET_NULL,null=True, blank=True)
    note = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Note entre 1 et 5 étoiles"
    )
    commentaire = models.TextField(blank=True)
    est_anonyme = models.BooleanField(default=False)
    est_approuve = models.BooleanField(default=False)  
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_updated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"Avis de {self.utilisateur.prenom} sur {self.plat.nom}"
    
    class Meta:
        unique_together = ['utilisateur', 'commande']
        ordering = ['-created_at']