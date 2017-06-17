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
    photo = forms.IntegerField(required=True, widget=forms.HiddenInput())
    album = forms.ModelChoiceField(
        required=True,
        empty_label=None,
        queryset=Album.objects.all(),
        widget=forms.Select(
            attrs={'id': 'album'}
        )
    )

    def update_album_cover(self, photo_id):
        try:
            album = self.cleaned_data.get('album')
            album.album_cover_id = photo_id
            album.save()
        except:
            raise ValidationError(_('Photo or the selected album doesn\’t exist.'))
