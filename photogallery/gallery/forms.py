from django import forms
from django.forms import ModelForm
from .models import Album, Photo
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

blank_choice = (('', '---------'),)


class NewAlbumForm(ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'description', 'parent', 'public']
        widgets = {
            'parent': forms.Select(attrs={'id': 'select'}),
        }


class EditAlbumForm(ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'description', 'parent', 'public']
        widgets = {
            'parent': forms.Select(attrs={'id': 'select'}),
        }


class NewPhotoForm(ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'description', 'album', 'image']
        widgets = {
            'album': forms.Select(attrs={'id': 'select'}),
        }


class EditPhotoForm(ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'description', 'album', 'image']
        widgets = {
            'album': forms.Select(attrs={'id': 'select'}),
        }


class MassUploadForm(ModelForm):
    class Meta:
        model = Photo
        fields = ['album', 'image']
        widgets = {
            'album': forms.Select(attrs={'id': 'select'}),
            'image': forms.ClearableFileInput(attrs={'multiple': True})
        }
