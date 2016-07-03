from django import forms
from django.forms import ModelForm
from .models import Album, Photo


class NewAlbumForm(ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'description', 'parent', 'public']
