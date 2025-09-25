from django.db import models
from django.utils import timezone

class CategoriePlat(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    couleur = models.CharField(max_length=7, default='#3B82F6')  # Code couleur HEX
    
    def __str__(self):
        return self.nom

class Plat(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField()
    categorie = models.ForeignKey(CategoriePlat, on_delete=models.SET_NULL, null=True, blank=True)
    allergenes = models.TextField(blank=True, help_text="Liste des allergènes présents")
    image = models.ImageField(upload_to='plats/', blank=True)
    est_actif = models.BooleanField(default=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Métadonnées
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('Utilisateurs.Utilisateur', on_delete=models.SET_NULL, null=True, blank=True)
    is_updated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    updated_by = models.IntegerField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return f"{self.nom} "
    
    class Meta:
        ordering = ['categorie', 'nom']