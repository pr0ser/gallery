import hashlib
import os
import shutil
from datetime import date
from glob import glob

from PIL import Image, ImageOps
from background_task import background
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

sort_order_choices = (
    ('date', _('Date (ascending)')),
    ('-date', _('Date (descending)')),
    ('title', _('Title (ascending)')),
    ('-title', _('Title (descending)')),
)


@background
def async_create_images(photo_id):
    image = Photo.objects.get(id=photo_id)
    image.create_thumbnails()
    image.create_previews()
    image.ready = True
    image.save()


@background
def async_save_photo(photo_id):
    photo = Photo.objects.get(pk=photo_id)
    photo.save()


def scan_new_photos(album_id):
    album = Album.objects.get(pk=album_id)
    album_dir = os.path.join('photos', album.directory)
    existing_photos = Photo.objects.all().filter(album_id=album_id).values_list('image', flat=True)
    extensions = ['.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG']
    os.chdir(settings.MEDIA_ROOT)
    all_photos = glob(os.path.join(album_dir, '*'))
    errors = []
    for photo in all_photos:
        extension = os.path.splitext(photo)[1]
        if photo not in existing_photos and extension in extensions:
            try:
                new_photo = Photo(
                    title=os.path.splitext(os.path.basename(photo))[0],
                    album_id=album_id,
                    image=photo,
                    ready=False)
                new_photo.save()
            except Exception as e:
                errors.append(_('Unable to add photo %(photo_name)s to album: %(error_message)s')
                              % {'photo_name': os.path.basename(photo), 'error_message': e})
    return errors


def calc_hash(filename):
    hash_sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def auto_orient(image):
    if hasattr(image, '_getexif'):
        try:
            exif = image._getexif()
        except Exception:
            exif = None
        if exif is not None:
            orientation = exif.get(0x0112, 1)
            if 1 <= orientation <= 8:
                operations = {
                    1: (),
                    2: (Image.FLIP_LEFT_RIGHT,),
                    3: (Image.ROTATE_180,),
                    4: (Image.ROTATE_180, Image.FLIP_LEFT_RIGHT),
                    5: (Image.ROTATE_270, Image.FLIP_LEFT_RIGHT),
                    6: (Image.ROTATE_270,),
                    7: (Image.ROTATE_90, Image.FLIP_LEFT_RIGHT),
                    8: (Image.ROTATE_90,),
                }
                for operation in operations[orientation]:
                    image = image.transpose(operation)
    return image


def validate_album_title(value):
    invalid_names = ['new', 'edit', 'delete', 'large']
    if value in invalid_names:
        raise ValidationError(
            _('%(value)s is not allowed album name.'),
            params={'value': value},
        )


def validate_photo_title(value):
    invalid_names = ['new', 'edit', 'delete', 'massupload']
    existing_name = Photo.objects.filter(title=value).exists()
    if value in invalid_names or existing_name:
        raise ValidationError(
            _('%(value)s is not allowed photo title.'),
            params={'value': value},
        )


class Album(models.Model):
    parent = models.ForeignKey('self', related_name='subalbums', null=True, blank=True, verbose_name=_('Parent'))
    title = models.CharField(_('Title'), max_length=255, unique=True, validators=[validate_album_title])
    date = models.DateField(_('Date'), default=date.today)
    description = models.TextField(_('Description'), blank=True)
    directory = models.SlugField(_('Directory'), unique=True)
    album_cover = models.OneToOneField(
        'Photo',
        related_name='Photo',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Album cover'))
    sort_order = models.CharField(
        _('Sort order'),
        max_length=255,
        choices=sort_order_choices,
        help_text=_('Sort order of photos in this album'),
        default='title')
    public = models.BooleanField(_('Public'), default=True)

    def get_absolute_url(self):
        return reverse('gallery:album', kwargs={'slug': self.directory})

    def delete_album_dirs(self):
        dirs = [os.path.join(settings.MEDIA_ROOT, 'photos', self.directory),
                os.path.join(settings.MEDIA_ROOT, 'previews', self.directory)]
        for d in dirs:
            if os.path.isdir(d):
                try:
                    shutil.rmtree(d)
                except OSError:
                    raise ValidationError(_('Unable to delete album directories.'))

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.directory = slugify(self.title)
        super(Album, self).save(*args, **kwargs)

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
    def pending_photos(self):
        pending = Photo.objects.filter(album_id=self.id).filter(ready=False).count()
        return pending
    pending_photos.short_description = _("Pending photos")

    class Meta:
        verbose_name = _('album')
        verbose_name_plural = _('albums')
        ordering = ('-date',)


class Photo(models.Model):
    def upload_dir(instance, filename):
        return 'photos/%s/%s' % (instance.album.directory, instance.image.name)

    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos', verbose_name=_('Album'))
    title = models.CharField(_('Title'), max_length=255, unique=True)
    slug = models.SlugField(_('Slug'), unique=True)
    date = models.DateTimeField(_('Date'), auto_now_add=True)
    image = models.ImageField(_('Image file'), upload_to=upload_dir)
    description = models.TextField(_('Description'), blank=True)
    file_hash = models.CharField(_('SHA-256'), max_length=255, blank=True)
    ready = models.BooleanField(_('Ready'), default=True)
    preview_img = models.ImageField(_('Preview image'), blank=True)
    hidpi_preview_img = models.ImageField(_('High DPI preview image'), blank=True)
    thumbnail_img = models.ImageField(_('Thumbnail image'), blank=True)
    hidpi_thumbnail_img = models.ImageField(_('High DPI thumbnail image'), blank=True)

    def get_absolute_url(self):
        return reverse('gallery:photo', kwargs={'slug': self.slug})

    def filename(self):
        return os.path.basename(self.image.name)

    def preview_filename(self):
        fname = os.path.basename(self.image.name)
        return 'preview_' + fname

    def hidpi_preview_filename(self):
        fname = os.path.basename(self.image.name)
        return 'hidpipreview_' + fname

    def thumbnail_img_filename(self):
        fname = os.path.basename(self.image.name)
        return 'thumb_' + fname

    def hidpi_thumbnail_img_filename(self):
        fname = os.path.basename(self.image.name)
        return 'hidpithumb_' + fname

    @cached_property
    def next_photo(self):
        photo_list = list(
            Photo.objects.filter(album_id=self.album_id)
            .order_by(self.album.sort_order)
            .values_list('id', flat=True))
        current = photo_list.index(self.pk)
        try:
            next_item = photo_list[current + 1]
            return Photo.objects.get(pk=next_item)
        except IndexError:
            return None

    @cached_property
    def previous_photo(self):
        photo_list = list(
            Photo.objects.filter(album_id=self.album_id)
            .order_by(self.album.sort_order)
            .values_list('id', flat=True))
        current = photo_list.index(self.pk)
        if current == 0:
            return None
        else:
            previous_item = photo_list[current - 1]
            return Photo.objects.get(pk=previous_item)

    def preview_dir(self):
        preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews', self.album.directory)
        if not os.path.exists(preview_dir):
            os.makedirs(preview_dir)
        return os.path.relpath(preview_dir, start=settings.MEDIA_ROOT)

    def create_preview_image(self, size, quality, output_file):
        image = auto_orient(Image.open(self.image.path))
        max_size = (size, size)
        image.thumbnail(size=max_size, resample=Image.LANCZOS)
        image.save(
            fp=os.path.join(settings.MEDIA_ROOT, self.preview_dir(), output_file),
            format='JPEG',
            quality=quality,
            icc_profile=image.info.get('icc_profile'),
            optimize=True,
            progressive=True)

    def create_thumbnail(self, size, quality, output_file):
        image = auto_orient(Image.open(self.image.path))
        width = size
        height = size
        image = ImageOps.fit(
            image=image,
            size=(width, height),
            method=Image.LANCZOS,
            bleed=0,
            centering=(0.5, 0.5))
        image.save(
            fp=os.path.join(settings.MEDIA_ROOT, self.preview_dir(), output_file),
            format='JPEG',
            quality=quality,
            icc_profile=image.info.get('icc_profile'),
            optimize=True,
            progressive=True)

    def create_previews(self):
        if self.image.height > 1327 or self.image.width > 1327:
            self.create_preview_image(size=1327, quality=90, output_file=self.preview_filename())
            self.preview_img = os.path.join(self.preview_dir(), self.preview_filename())
        if self.image.height > 2340 or self.image.width > 2340:
            self.create_preview_image(size=2340, quality=90, output_file=self.hidpi_preview_filename())
            self.hidpi_preview_img = os.path.join(self.preview_dir(), self.hidpi_preview_filename())

    def create_thumbnails(self):
        self.create_thumbnail(size=330, quality=80, output_file=self.thumbnail_img_filename())
        self.thumbnail_img = os.path.join(self.preview_dir(), self.thumbnail_img_filename())
        self.create_thumbnail(size=600, quality=80, output_file=self.hidpi_thumbnail_img_filename())
        self.hidpi_thumbnail_img = os.path.join(self.preview_dir(), self.hidpi_thumbnail_img_filename())

    def __str__(self):
        return self.title

    def admin_thumbnail(self):
        if self.ready:
            img_url = self.thumbnail_img.url
            link = self.get_absolute_url()
            return mark_safe(f'<a href={link}><img src="{img_url}" width="100" height="100" alt="Thumbnail"/></a>')
        else:
            return None
    admin_thumbnail.short_description = _("Thumbnail")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Photo, self).save(*args, **kwargs)
        if calc_hash(self.image.path) != self.file_hash:
            self.file_hash = calc_hash(self.image.path)
            if not self.ready:
                async_create_images(self.id)
            else:
                self.create_previews()
                self.create_thumbnails()
            super(Photo, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('photo')
        verbose_name_plural = _('photos')
        ordering = ('-date',)
