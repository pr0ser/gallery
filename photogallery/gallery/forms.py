from django import forms
from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm, widgets
from django.utils.translation import ugettext_lazy as _

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


class AlbumCoverPhotoForm(Form):
    photo = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    album = forms.IntegerField(
        widget=forms.Select(
            choices=Album.objects.all().values_list('id', 'title'),
            attrs={'id': 'album'}
        )
    )

    def update_album_cover(self, photo_id):
        if Photo.objects.filter(pk=photo_id).exists() and Album.objects.filter(pk=self.cleaned_data['album']).exists():
            album = Album.objects.get(id=self.cleaned_data['album'])
            album.album_cover_id = photo_id
            album.save()
        else:
            raise ValidationError(_('Invalid data. Photo or the selected album doesn\’t exist.'))
