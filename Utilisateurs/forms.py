from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm, UserChangeForm
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from .models import Utilisateur, Profile, ROLE_CHOICES, SITE_CHOICES, DEPARTEMENT_CHOICES

User = get_user_model()

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Adresse e-mail",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adresse e-mail',
            'id': 'id_email'
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe',
            'id': 'id_password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label="Se souvenir de moi",
        widget=forms.CheckboxInput(attrs={
            'id': 'id_remember_me'
        })
    )

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            # Authentifier avec l'email
            self.user_cache = authenticate(self.request, email=email, password=password)  
            
            if self.user_cache is None:
                raise ValidationError(
                    "Email ou mot de passe incorrect.",
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

class CustomUserCreationForm(UserCreationForm):
    prenom = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    nom = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Nom'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adresse e-mail'
        })
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        initial='collaborateur',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    qid = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'QID (optionnel)'
        })
    )
    site = forms.ChoiceField(
        choices=SITE_CHOICES,
        initial='Danga',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    departement = forms.ChoiceField(
        choices=DEPARTEMENT_CHOICES,
        initial='Autres',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    terms = forms.BooleanField(
        required=True,
        label="J'accepte les conditions d'utilisation et la politique de confidentialité",
        widget=forms.CheckboxInput(attrs={
            'id': 'terms'
        })
    )

    class Meta:
        model = User
        fields = ('prenom', 'nom', 'email', 'role', 'qid', 'site', 'departement', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse e-mail est déjà utilisée.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    password = None
    
    prenom = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    nom = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Nom'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adresse e-mail'
        })
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    qid = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'QID'
        })
    )
    site = forms.ChoiceField(
        choices=SITE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    departement = forms.ChoiceField(
        choices=DEPARTEMENT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ('prenom', 'nom', 'email', 'role', 'qid', 'site', 'departement')

class ProfileUpdateForm(forms.ModelForm):
    prenom = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    nom = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Nom'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adresse e-mail'
        })
    )
    site = forms.ChoiceField(
        choices=SITE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    departement = forms.ChoiceField(
        choices=DEPARTEMENT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ['prenom', 'nom', 'email', 'site', 'departement']

class AdminUserUpdateForm(forms.ModelForm):
    prenom = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    nom = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Nom'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adresse e-mail'
        })
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    qid = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'QID'
        })
    )
    site = forms.ChoiceField(
        choices=SITE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    departement = forms.ChoiceField(
        choices=DEPARTEMENT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ['prenom', 'nom', 'email', 'role', 'qid', 'site', 'departement']

class ProfileForm(forms.ModelForm):
    telephone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Téléphone'
        })
    )
    
    class Meta:
        model = Profile
        fields = ['telephone']

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label="Ancien mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ancien mot de passe'
        })
    )
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nouveau mot de passe'
        })
    )
    new_password2 = forms.CharField(
        label="Confirmer le nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmer le nouveau mot de passe'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise forms.ValidationError("L'ancien mot de passe est incorrect.")
        return old_password

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")
        
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        
        return new_password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adresse e-mail'
        })
    )

class ThemeToggleForm(forms.Form):
    theme_sombre = forms.BooleanField(
        required=False,
        widget=forms.HiddenInput()
    )

class UserSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par nom, prénom, email...'
        })
    )
    role = forms.ChoiceField(
        choices=[('', 'Tous les rôles')] + list(ROLE_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    site = forms.ChoiceField(
        choices=[('', 'Tous les sites')] + list(SITE_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    departement = forms.ChoiceField(
        choices=[('', 'Tous les départements')] + list(DEPARTEMENT_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )