from datetime import date
from glob import glob
from json import loads as jsonloads
from logging import getLogger
from os import path, makedirs, chdir
from shutil import rmtree
from string import ascii_lowercase

from PIL import Image, ImageOps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.timezone import make_aware, get_current_timezone
from django.utils.translation import ugettext_lazy as _
from django_celery_results.models import TaskResult

from .exif_reader import ExifInfo
from .tasks import post_process_image
from .utils import calc_hash, auto_orient, get_geocoding

log = getLogger(__name__)


def validate_album_title(value):
    invalid_names = ['new']
    if value in invalid_names:
        raise ValidationError(
            _('%(value)s is not allowed album name.'),
            params={'value': value},
        )


def validate_photo_title(value):
    invalid_names = ['new']
    existing_name = Photo.objects.filter(title=value).exists()
    if value in invalid_names or existing_name:
        raise ValidationError(
            _('%(value)s is not allowed photo title.'),
            params={'value': value},
        )


class Album(models.Model):
    sort_order_choices = (
        ('date', _('Date (ascending)')),
        ('-date', _('Date (descending)')),
        ('title', _('Title (ascending)')),
        ('-title', _('Title (descending)')),
    )
    parent = models.ForeignKey(
        'self', related_name='subalbums',
        null=True,
        blank=True,
        verbose_name=_('Parent'),
        on_delete=models.CASCADE
    )
    title = models.CharField(
        _('Title'),
        max_length=255,
        unique=True,
        validators=[validate_album_title]
    )
    date = models.DateField(
        _('Date'),
        default=date.today
    )
    description = models.TextField(
        _('Description'),
        blank=True
    )
    directory = models.SlugField(
        _('Directory'),
        unique=True
    )
    album_cover = models.OneToOneField(
        'Photo',
        related_name='Photo',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Album cover')
    )
    sort_order = models.CharField(
        _('Sort order'),
        max_length=255,
        choices=sort_order_choices,
        help_text=_('Sort order of photos in this album'),
        default='title'
    )
    public = models.BooleanField(
        _('Public'),
        default=True
    )
    downloadable = models.BooleanField(
        _('Allow ZIP download'),
        default=False
    )
    show_metadata = models.BooleanField(
        _('Show EXIF metadata'),
        default=True
    )
    show_location = models.BooleanField(
        _('Show location information'),
        default=True
    )

    class Meta:
        verbose_name = _('album')
        verbose_name_plural = _('albums')
        ordering = ('-date',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.directory:
            self.directory = slugify(self.title)
        super(Album, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('gallery:album', kwargs={'slug': self.directory})

    def delete_album_dirs(self):
        dirs = [path.join(settings.MEDIA_ROOT, 'photos', self.directory),
                path.join(settings.MEDIA_ROOT, 'previews', self.directory)]
        for d in dirs:
            if path.isdir(d):
                try:
                    rmtree(d)
                except OSError:
                    raise ValidationError(_('Unable to delete album directories.'))

    def delete(self, *args, **kwargs):
        super(Album, self).delete(*args, **kwargs)
        self.delete_album_dirs()

    def parent_albums(self):
        albums = []
        current_album = self.parent
        while current_album is not None:
            albums.append(current_album)
            current_album = current_album.parent
        return albums

    @cached_property
    def pending_post_processing(self):
        post_processing = Photo.objects.filter(album_id=self.id).filter(ready=False).count()
        return post_processing
    pending_post_processing.short_description = _("Photos pending post-processing")

    @cached_property
    def pending_updates(self):
        task = (
            TaskResult.objects
            .filter(status='PROGRESS')
            .filter(result__contains=self.directory)
            .first()
        )
        if task:
            content = jsonloads(task.result)
            if content['album'] == self.directory:
                return content['total'] - content['current']
        return 0
    pending_updates.short_description = _("Photos pending updates")

    @property
    def media_dir(self):
        album_dir = path.join('photos', self.directory)
        return album_dir

    def get_photos_in_dir(self):
        chdir(settings.MEDIA_ROOT)
        extensions = ['*.jpg', '*.jpeg', '*.png']
        photos = []
        for ext in extensions:
            photos.extend(glob(path.join(self.media_dir, ext)))
            photos.extend(glob(path.join(self.media_dir, ext.upper())))
        return photos

    def scan_new_photos(self):
        existing_photos = (
            Photo.objects
            .all()
            .filter(album_id=self.pk)
            .values_list('image', flat=True)
        )
        all_photos = self.get_photos_in_dir()
        new_photos = 0
        errors = ''
        for photo in all_photos:
            if photo not in existing_photos:
                try:
                    new_photo = Photo(
                        title=path.splitext(path.basename(photo))[0],
                        album_id=self.pk,
                        image=photo,
                        ready=False)
                    new_photo.save()
                    new_photos += 1
                except Exception as e:
                    errors += _('Failed to add photo %(filename)s to album.') \
                              % {'filename': path.basename(photo)}
                    log.error(f'Failed to add photo {path.basename(photo)}: {e}')
        return new_photos, errors

    def admin_thumbnail(self):
        if self.album_cover_id:
            img_url = self.album_cover.thumbnail_img.url
            link = self.get_absolute_url()
            return mark_safe(
                f'<a href={link}>'
                f'<img src="{img_url}"'
                f'width="100"'
                f'height="100"'
                f'alt="Thumbnail"/>'
                f'</a>'
            )
        else:
            return None
    admin_thumbnail.short_description = _("Cover photo")


class Photo(models.Model):
    def upload_dir(instance, filename):
        return 'photos/%s/%s' % (instance.album.directory, instance.image.name)

    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name=_('Album')
    )
    title = models.CharField(
        _('Title'),
        max_length=100,
        unique=False
    )
    slug = models.SlugField(
        _('Slug'),
        unique=True,
        max_length=100
    )
    date = models.DateTimeField(
        _('Date'),
        auto_now_add=True
    )
    image = models.ImageField(
        _('Image file'),
        upload_to=upload_dir,
        max_length=100
    )
    description = models.TextField(
        _('Description'),
        blank=True
    )
    file_hash = models.CharField(
        _('SHA-256'),
        max_length=255,
        blank=True
    )
    ready = models.BooleanField(
        _('Ready'),
        default=True
    )
    preview_img = models.ImageField(
        _('Preview image'),
        blank=True,
        max_length=150
    )
    hidpi_preview_img = models.ImageField(
        _('High DPI preview image'),
        blank=True,
        max_length=150
    )
    thumbnail_img = models.ImageField(
        _('Thumbnail image'),
        blank=True,
        max_length=150
    )
    hidpi_thumbnail_img = models.ImageField(
        _('High DPI thumbnail image'),
        blank=True,
        max_length=150)

    class Meta:
        verbose_name = _('photo')
        verbose_name_plural = _('photos')
        ordering = ('-date',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        if self.is_existing_slug():
            self.slug = self.slug + '-' + get_random_string(length=5, allowed_chars=ascii_lowercase)
        super(Photo, self).save(*args, **kwargs)
        if calc_hash(self.image.path) != self.file_hash:
            self.file_hash = calc_hash(self.image.path)
            if not self.ready:
                post_process_image.delay(self.id)
            else:
                self.create_previews()
                self.create_thumbnails()
                self.save_exif_data()
                super(Photo, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('gallery:photo', kwargs={'slug': self.slug})

    @property
    def preview_filename(self):
        fname = path.basename(self.image.name)
        return 'preview_' + fname

    @property
    def hidpi_preview_filename(self):
        fname = path.basename(self.image.name)
        return 'hidpipreview_' + fname

    @property
    def thumbnail_img_filename(self):
        fname = path.basename(self.image.name)
        return 'thumb_' + fname

    @property
    def hidpi_thumbnail_img_filename(self):
        fname = path.basename(self.image.name)
        return 'hidpithumb_' + fname

    @cached_property
    def current_ordering(self):
        photo_list = list(
            Photo.objects.filter(album_id=self.album_id)
            .order_by(self.album.sort_order)
            .values_list('id', flat=True)
        )
        return photo_list

    @cached_property
    def next_photo(self):
        photo_list = self.current_ordering
        current = photo_list.index(self.pk)
        try:
            next_item = photo_list[current + 1]
            return Photo.objects.get(pk=next_item)
        except IndexError:
            return None

    @cached_property
    def previous_photo(self):
        photo_list = self.current_ordering
        current = photo_list.index(self.pk)
        if current == 0:
            return None
        else:
            previous_item = photo_list[current - 1]
            return Photo.objects.get(pk=previous_item)

    def preview_dir(self):
        preview_dir = path.join(settings.MEDIA_ROOT, 'previews', self.album.directory)
        if not path.exists(preview_dir):
            makedirs(preview_dir)
        return path.relpath(preview_dir, start=settings.MEDIA_ROOT)

    def create_preview_image(self, size, quality, output_file):
        image = auto_orient(Image.open(self.image.path))
        max_size = (size, size)
        image.thumbnail(size=max_size, resample=Image.LANCZOS)
        image.save(
            fp=path.join(settings.MEDIA_ROOT, self.preview_dir(), output_file),
            format=image.format,
            quality=quality,
            icc_profile=image.info.get('icc_profile'),
            optimize=True,
            progressive=True
        )

    def create_thumbnail(self, size, quality, output_file):
        image = auto_orient(Image.open(self.image.path))
        width = size
        height = size
        image = ImageOps.fit(
            image=image,
            size=(width, height),
            method=Image.LANCZOS,
            bleed=0,
            centering=(0.5, 0.5)
        )
        image.save(
            fp=path.join(settings.MEDIA_ROOT, self.preview_dir(), output_file),
            format=image.format,
            quality=quality,
            icc_profile=image.info.get('icc_profile'),
            optimize=True,
            progressive=True
        )

    def create_previews(self):
        if self.image.height > 1327 or self.image.width > 1327:
            self.create_preview_image(
                size=1327,
                quality=90,
                output_file=self.preview_filename
            )
            self.preview_img = path.join(
                self.preview_dir(),
                self.preview_filename
            )
        if self.image.height > 2340 or self.image.width > 2340:
            self.create_preview_image(
                size=2340,
                quality=90,
                output_file=self.hidpi_preview_filename
            )
            self.hidpi_preview_img = path.join(
                self.preview_dir(),
                self.hidpi_preview_filename
            )

    def create_thumbnails(self):
        self.create_thumbnail(
            size=380,
            quality=80,
            output_file=self.thumbnail_img_filename
        )
        self.thumbnail_img = path.join(
            self.preview_dir(),
            self.thumbnail_img_filename
        )
        self.create_thumbnail(
            size=600,
            quality=80,
            output_file=self.hidpi_thumbnail_img_filename
        )
        self.hidpi_thumbnail_img = path.join(
            self.preview_dir(),
            self.hidpi_thumbnail_img_filename
        )

    def is_existing_slug(self):
        try:
            photo = Photo.objects.get(slug=self.slug)
            if photo.pk != self.pk:
                return True
        except Exception:
            return False

    def save_exif_data(self):
        try:
            exif_data = ExifInfo(self.image.path)
            if exif_data.has_exif_data:
                tz_date = make_aware(exif_data.time_taken, get_current_timezone())
                data = ExifData(
                    photo=Photo.objects.get(pk=self.id),
                    date_taken=tz_date,
                    make=exif_data.make,
                    model=exif_data.model,
                    iso=exif_data.iso,
                    shutter_speed=exif_data.shutter_speed,
                    aperture=exif_data.aperture,
                    focal_length=exif_data.focal_length,
                    lens=exif_data.lens
                )

                if exif_data.has_location:
                    data.has_location = True
                    data.latitude = exif_data.latitude
                    data.longitude = exif_data.longitude
                    data.altitude = exif_data.altitude
                    data.get_locality_and_country()
                data.save()
        except Exception as e:
            log.error(f'Failed to save EXIF data for file {self.image.path}: {e}')

    def admin_thumbnail(self):
        if self.ready:
            img_url = self.thumbnail_img.url
            link = self.get_absolute_url()
            return mark_safe(
                f'<a href={link}>'
                f'<img src="{img_url}"'
                f'width="100"'
                f'height="100"'
                f'alt="Thumbnail"/>'
                f'</a>'
            )
        else:
            return None
    admin_thumbnail.short_description = _("Thumbnail")


class ExifData(models.Model):
    photo = models.OneToOneField(
        Photo,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name=_('Photo')
    )
    date_taken = models.DateTimeField(
        _('Date/Time taken'),
        auto_now_add=False,
        blank=True,
        null=True
    )
    has_location = models.BooleanField(
        _('Has location'),
        default=False
    )
    make = models.CharField(
        _('Manufacturer'),
        max_length=100,
        blank=True,
        null=True
    )
    model = models.CharField(
        _('Model'),
        max_length=100,
        blank=True,
        null=True
    )
    iso = models.PositiveIntegerField(
        _('ISO speed'),
        blank=True,
        null=True
    )
    shutter_speed = models.CharField(
        _('Shutter speed'),
        max_length=50,
        blank=True,
        null=True
    )
    aperture = models.DecimalField(
        _('Aperture'),
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True
    )
    focal_length = models.DecimalField(
        _('Focal length'),
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True
    )
    lens = models.CharField(
        _('Lens'),
        max_length=200,
        blank=True,
        null=True
    )
    latitude = models.DecimalField(
        _('Latitude'),
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )
    longitude = models.DecimalField(
        _('Longitude'),
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )
    altitude = models.IntegerField(
        _('Altitude'),
        blank=True,
        null=True
    )
    locality = models.CharField(
        _('Locality'),
        max_length=200,
        blank=True,
        null=True
    )
    country = models.CharField(
        _('Country'),
        max_length=200,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('EXIF data')
        verbose_name_plural = _('EXIF data')
        ordering = ('-date_taken',)

    def __str__(self):
        return self.photo.title

    def get_absolute_url(self):
        return reverse('gallery:photo', kwargs={'slug': self.photo.slug})

    def get_locality_and_country(self):
        try:
            self.locality, self.country = get_geocoding(self.latitude, self.longitude)
        except Exception:
            pass

    def update_geocoding(self, overwrite=False):
        if overwrite:
            if self.has_location:
                try:
                    self.locality, self.country = get_geocoding(self.latitude, self.longitude)
                    self.save()
                except Exception as e:
                    log.error(f'Failed to update geocoding for photo {self.photo.title}: {e}')
        else:
            if self.has_location and not self.locality and not self.country:
                try:
                    self.locality, self.country = get_geocoding(self.latitude, self.longitude)
                    self.save()
                except Exception as e:
                    log.error(f'Failed to update geocoding for photo {self.photo.title}: {e}')

    def admin_thumbnail(self):
        if self.photo.ready:
            img_url = self.photo.thumbnail_img.url
            link = self.photo.get_absolute_url()
            return mark_safe(
                f'<a href={link}>'
                f'<img src="{img_url}"'
                f'width="100"'
                f'height="100"'
                f'alt="Thumbnail"/>'
                f'</a>'
            )
        else:
            return None
    admin_thumbnail.short_description = _("Thumbnail")
