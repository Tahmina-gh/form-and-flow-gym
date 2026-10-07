import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Lead, TourRequest, ContactMessage

class NoSpam(forms.Form):
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={'style': 'display:none', 'tabindex': '-1', 'autocomplete': 'off'}))
    def clean_website(self):
        if self.cleaned_data.get('website'): raise forms.ValidationError('Spam detected.')

def clean_phone(v):
    if not re.fullmatch(r'\+?[0-9 \-]{7,20}', v or ''): raise forms.ValidationError('Enter a valid phone number.')
    return v

class SignupForm(UserCreationForm):
    class Meta: model = User; fields = ('username', 'email', 'first_name', 'phone')
    def clean_email(self):
        e = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=e).exists(): raise forms.ValidationError('An account with this email already exists.')
        return e

class ProfileForm(forms.ModelForm):
    class Meta: model = User; fields = ('first_name', 'last_name', 'phone', 'photo')

class LeadForm(NoSpam, forms.ModelForm):
    preferred_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta: model = Lead; fields = ('name', 'email', 'phone', 'age', 'goal', 'preferred_date', 'preferred_time', 'level')
    def clean_phone(self): return clean_phone(self.cleaned_data['phone'])

class TourForm(NoSpam, forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'})); time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    class Meta: model = TourRequest; fields = ('name', 'email', 'phone', 'date', 'time')
    def clean_phone(self): return clean_phone(self.cleaned_data['phone'])

class ContactForm(NoSpam, forms.ModelForm):
    class Meta: model = ContactMessage; fields = ('name', 'email', 'phone', 'message')

class QuizForm(forms.Form):
    goal = forms.ChoiceField(choices=[('muscle', 'Build muscle'), ('weight', 'Lose weight'), ('strength', 'Improve strength'), ('endurance', 'Improve endurance'), ('mobility', 'Improve mobility'), ('general', 'General fitness')])
    level = forms.ChoiceField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')])
    days = forms.IntegerField(min_value=1, max_value=7, label='Days per week')
