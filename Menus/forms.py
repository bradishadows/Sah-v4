from django import forms
from django.forms import modelformset_factory
from .models import Menu, MenuPlat
from Plats.models import Plat

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['titre', 'description', 'date_limite_commande', 'est_publie']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du menu'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description du menu'
            }),
            'date_limite_commande': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'est_publie': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class MenuPlatForm(forms.ModelForm):
    plat = forms.ModelChoiceField(
        queryset=Plat.objects.filter(est_actif=True, is_deleted=False),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Plat"
    )

    class Meta:
        model = MenuPlat
        fields = ['plat', 'prix', 'quantite_max']
        widgets = {
            'prix': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'quantite_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            })
        }

MenuPlatFormSet = modelformset_factory(
    MenuPlat,
    form=MenuPlatForm,
    extra=1,
    can_delete=True
)
