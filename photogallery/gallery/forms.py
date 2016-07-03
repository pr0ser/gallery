from django import forms
from django.forms import ModelForm
from .models import Album, Photo


class LoginForm(forms.Form):
    username = forms.CharField(label='käyttäjätunnus', max_length=100)
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        label='salasana',
        max_length=100)
