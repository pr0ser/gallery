import hashlib
import os
import shutil
from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from wand.image import Image

sort_order_choices = (
    ('date', _('Date (ascending)')),
    ('-date', _('Date (descending)')),
    ('title', _('Title (ascending)')),
    ('-title', _('Title (descending)')),
)


def calc_hash(filename):
    hash_sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def validate_album_title(value):
    invalid_names = ['new', 'edit', 'delete', 'updatecover']
    if value in invalid_names:
        raise ValidationError(
            _('%(value)s is not allowed title name.'),
            params={'value': value},
        )


class Album(models.Model):
    parent = models.ForeignKey('self', related_name='subalbums', null=True, blank=True, verbose_name=_('Parent'))
    title = models.CharField(_('Title'), max_length=255, unique=True, validators=[validate_album_title])
    date = models.DateField(_('Date'), default=date.today)
    description = models.TextField(_('Description'), blank=True)
    directory = models.SlugField(_('Directory'), unique=True)
    album_cover = models.OneToOneField('Photo',
                                       related_name='Photo',
                                       null=True,
                                       blank=True,
                                       on_delete=models.SET_NULL,
                                       verbose_name=_('Album cover'))
    sort_order = models.CharField(_('Sort order'),
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

    def next_photo(self):
        photo_list = list(Photo.objects.filter(album_id=self.album_id)
                          .order_by(self.album.sort_order)
                          .values_list('id', flat=True))
        current = photo_list.index(self.pk)
        try:
            next_item = photo_list[current + 1]
            return Photo.objects.get(pk=next_item)
        except IndexError:
            return None

    def previous_photo(self):
        photo_list = list(Photo.objects.filter(album_id=self.album_id)
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

    def is_landscape(self):
        if self.image.width > self.image.height:
            return True
        else:
            return False

    def create_preview_image(self, size, quality, output_filename):
        if self.image.width < self.image.height:
            long_side = 'x{}'.format(size)
        else:
            long_side = '{}x'.format(size)
        with Image(filename=self.image.path) as img:
            img.transform(resize=long_side)
            if img.format == 'JPEG':
                img.compression_quality = quality
            img.save(filename=os.path.join(settings.MEDIA_ROOT, self.preview_dir(), output_filename))

    def create_thumbnail(self, size, quality, image_filename):
        if self.image.width > self.image.height:
            long_side = 'x{}'.format(size)
        else:
            long_side = '{}x'.format(size)
        with Image(filename=self.image.path) as img:
            img.transform(resize=long_side)
            img.crop(width=size, height=size, gravity='center')
            if img.format == 'JPEG':
                img.compression_quality = quality
            img.save(filename=os.path.join(settings.MEDIA_ROOT, self.preview_dir(), image_filename))

    def create_previews(self):
        if self.image.height > 1327 or self.image.width > 1327:
            self.create_preview_image(size='1327', quality=85, output_filename=self.preview_filename())
            self.preview_img = os.path.join(self.preview_dir(), self.preview_filename())
        if self.image.height > 2340 or self.image.width > 2340:
            self.create_preview_image(size='2340', quality=85, output_filename=self.hidpi_preview_filename())
            self.hidpi_preview_img = os.path.join(self.preview_dir(), self.hidpi_preview_filename())

    def create_thumbnails(self):
        self.create_thumbnail(size=330, quality=75, image_filename=self.thumbnail_img_filename())
        self.thumbnail_img = os.path.join(self.preview_dir(), self.thumbnail_img_filename())
        self.create_thumbnail(size=600, quality=75, image_filename=self.hidpi_thumbnail_img_filename())
        self.hidpi_thumbnail_img = os.path.join(self.preview_dir(), self.hidpi_thumbnail_img_filename())

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Photo, self).save(*args, **kwargs)
        if calc_hash(self.image.path) != self.file_hash:
            self.file_hash = calc_hash(self.image.path)
            self.create_previews()
            self.create_thumbnails()
            super(Photo, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('photo')
        verbose_name_plural = _('photos')
        ordering = ('-date',)
