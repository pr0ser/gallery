from os import path

from django import forms
from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm, widgets
from django.utils.translation import ugettext_lazy as _

from .models import Album, Photo, ExifData

blank_choice = (('', ''),)


class CustomDateInput(widgets.TextInput):
    input_type = 'date'


class NewAlbumForm(ModelForm):
    class Meta:
        model = Album
        fields = [
            'title',
            'description',
            'date',
            'parent',
            'sort_order',
            'public',
            'downloadable',
            'show_metadata',
            'show_location'
        ]
        widgets = {
            'parent': forms.Select(attrs={'id': 'parent'}),
            'sort_order': forms.Select(attrs={'id': 'sort_order'}),
            'date': CustomDateInput,
        }


class EditAlbumForm(ModelForm):
    class Meta:
        model = Album
        fields = [
            'title',
            'description',
            'date',
            'parent',
            'sort_order',
            'public',
            'downloadable',
            'show_metadata',
            'show_location'
        ]
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

    def clean_title(self):
        title = self.cleaned_data.get('title')
        invalid_names = ['new', 'edit', 'delete', 'massupload']
        existing_name = Photo.objects.filter(title=title).exists()
        if title in invalid_names or existing_name:
            raise ValidationError(
                _('%(value)s is not allowed photo title.'),
                params={'value': title},
            )
        return title


class EditPhotoForm(ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'description']
        widgets = {
            'album': forms.Select(attrs={'id': 'album'}),
        }


class MassUploadForm(ModelForm):
    class Meta:
        model = Photo
        fields = ['album', 'image']
        labels = {
            'album': _('Album'),
            'image': _('Images')
        }
        widgets = {
            'album': forms.Select(attrs={'id': 'select'}),
            'image': forms.ClearableFileInput(attrs={'multiple': True})
        }

    def clean_image(self):
        files = self.files.getlist('image')
        for file in files:
            extension_name = path.splitext(file.name)[1]
            valid_extensions = ['.jpg', '.jpeg', '.png']
            if extension_name.lower() not in valid_extensions:
                raise ValidationError(
                    _('%(value)s files are not supported.'),
                    params={'value': extension_name})
        return files


class AlbumCoverPhotoForm(Form):
    album = forms.ModelChoiceField(
        label=_('Album'),
        required=True,
        empty_label=None,
        queryset=Album.objects.all(),
        widget=forms.Select(
            attrs={'id': 'album'}
        )
    )

    def update_album_cover(self, photo_slug):
        try:
            photo = Photo.objects.get(slug=photo_slug)
            album = self.cleaned_data.get('album')
            album.album_cover_id = photo.id
            album.save()
        except Exception:
            raise ValidationError(_('Photo or the selected album doesn\’t exist.'))


class EditExifDataForm(ModelForm):
    class Meta:
        model = ExifData
        fields = [
            'make',
            'model',
            'iso',
            'shutter_speed',
            'aperture',
            'focal_length',
            'lens',
            'latitude',
            'longitude',
            'locality',
            'country',
        ]

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")
        error_msg = _('Latitude and longitude must both have values or be both empty.')

        if (latitude and not longitude) or (longitude and not latitude):
            self.add_error('latitude', error_msg)
            self.add_error('longitude', error_msg)
