from django import forms
from .models import CategoriePlat, Plat

class CategoriePlatForm(forms.ModelForm):
    class Meta:
        model = CategoriePlat
        fields = ['nom', 'description', 'couleur']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la catégorie'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description de la catégorie'
            }),
            'couleur': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'value': '#3B82F6'
            })
        }

class PlatForm(forms.ModelForm):
    class Meta:
        model = Plat
        fields = ['nom', 'description', 'categorie', 'allergenes', 'image', 'prix', 'est_actif']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du plat'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description du plat'
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-control'
            }),
            'allergenes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Liste des allergènes (séparés par des virgules)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'prix': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'est_actif': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
