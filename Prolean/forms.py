import re
import requests
from django import forms
from django.core.validators import MinLengthValidator, EmailValidator
from django.conf import settings
from .models import ContactRequest, TrainingReview , TrainingWaitlist


def _public_api_base_url():
    base = getattr(
        settings,
        'SITE_MANAGEMENT_PUBLIC_API_BASE',
        'https://sitemanagement-production.up.railway.app/api/public'
    )
    return base.rstrip('/')


def get_city_choices():
    try:
        response = requests.get(f"{_public_api_base_url()}/cities", timeout=8)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, list):
            choices = [(item.get('id'), item.get('name')) for item in payload if item.get('id') and item.get('name')]
            if choices:
                return choices
    except Exception:
        pass

    return [
        ('fallback-casa', 'Casablanca'),
        ('fallback-rabat', 'Rabat'),
        ('fallback-tanger', 'Tanger'),
    ]

class ContactRequestForm(forms.ModelForm):
    """Contact request form with validation"""
    class Meta:
        model = ContactRequest
        fields = ['full_name', 'email', 'phone', 'city', 'country', 
                  'request_type', 'message', 'training_title']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Votre nom complet',
                'minlength': '3',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'email@exemple.com',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+212 6 12 34 56 78',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Décrivez votre demande...',
                'rows': 4,
            }),
            'request_type': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if len(full_name) < 3:
            raise forms.ValidationError("Le nom doit contenir au moins 3 caractères.")
        return full_name
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        # Basic phone validation
        if phone and not any(char.isdigit() for char in phone):
            raise forms.ValidationError("Veuillez entrer un numéro de téléphone valide.")
        return phone

class TrainingReviewForm(forms.ModelForm):
    """Training review form"""
    class Meta:
        model = TrainingReview
        fields = ['full_name', 'email', 'rating', 'title', 'comment']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Votre nom',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Votre email',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Titre de votre avis',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Partagez votre expérience...',
                'rows': 4,
            }),
            'rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
        }
    
    def clean_comment(self):
        comment = self.cleaned_data.get('comment', '').strip()
        if len(comment) < 10:
            raise forms.ValidationError("Le commentaire doit contenir au moins 10 caractères.")
        return comment

class WaitlistForm(forms.ModelForm):
    """Waitlist form"""
    class Meta:
        model = TrainingWaitlist
        fields = ['email', 'full_name', 'phone', 'city']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'email@exemple.com',
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Votre nom complet',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+212 6 12 34 56 78',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Votre ville',
            }),
        }

class TrainingInquiryForm(forms.Form):
    """Training inquiry form"""
    training_id = forms.IntegerField(widget=forms.HiddenInput())
    full_name = forms.CharField(max_length=200, min_length=3)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    city = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100, initial='Maroc')
    message = forms.CharField(widget=forms.Textarea, required=False)

class MigrationInquiryForm(forms.Form):
    """Migration inquiry form"""
    first_name = forms.CharField(max_length=100, min_length=2)
    last_name = forms.CharField(max_length=100, min_length=2)
    email = forms.EmailField()
    current_country = forms.CharField(max_length=100)
    target_country = forms.CharField(max_length=100)
    profession = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea, required=False)

class StudentRegistrationForm(forms.Form):
    """Public registration form for students through management API."""
    full_name = forms.CharField(
        max_length=255,
        label="Nom complet",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nom complet'})
    )
    cin_or_passport = forms.CharField(
        max_length=20,
        required=False,
        label="CIN ou Passeport",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'CIN ou Passeport (Optionnel)'})
    )
    phone_number = forms.CharField(
        max_length=20,
        label="Telephone",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Telephone'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'email@exemple.com'})
    )
    city = forms.ChoiceField(
        choices=[],
        label="Ville",
        widget=forms.Select(attrs={'class': 'auth-input'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Mot de passe'})
    )
    confirm_password = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirmer le mot de passe'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].choices = [('', 'Selectionnez votre ville')] + get_city_choices()

    def clean_email(self):
        return self.cleaned_data.get('email')

    def clean_phone_number(self):
        return self.cleaned_data.get('phone_number')

    def clean_cin_or_passport(self):
        cin = self.cleaned_data.get('cin_or_passport')
        if cin:
            cin = cin.strip().upper()
            cin_regex = r'^[A-Z]{1,2}[0-9]{6}$'
            if not re.match(cin_regex, cin):
                raise forms.ValidationError("Format CIN invalide. Utilisez 1 ou 2 lettres suivies de 6 chiffres (ex: AB123456).")
        return cin

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data


class StudentLoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'auth-input', 'placeholder': 'email@exemple.com'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Mot de passe'})
    )

