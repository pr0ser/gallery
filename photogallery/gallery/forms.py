from django import forms
from django.forms import ModelForm
from django.forms import widgets

from gallery.models import Album, Photo

blank_choice = (('', ''),)


class CustomDateInput(widgets.TextInput):
    input_type = 'date'


class NewAlbumForm(ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'description', 'date', 'parent', 'sort_order', 'public']
        widgets = {
            'parent': forms.Select(attrs={'id': 'parent'}),
            'sort_order': forms.Select(attrs={'id': 'sort_order'}),
            'date': CustomDateInput,
        }


class EditAlbumForm(ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'description', 'date', 'parent', 'sort_order', 'public']
        widgets = {
            'parent': forms.Select(attrs={'id': 'parent'}),
            'sort_order': forms.Select(attrs={'id': 'sort_order'}),
            'date': CustomDateInput,
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
            'album': forms.Select(attrs={'id': 'album'}),
        }


class MassUploadForm(ModelForm):
    class Meta:
        model = Photo
        fields = ['album', 'image']
        widgets = {
            'album': forms.Select(attrs={'id': 'select'}),
            'image': forms.ClearableFileInput(attrs={'multiple': True})
        }
