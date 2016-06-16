from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from wand.image import Image
import os
import hashlib
from django.conf import settings


def calc_hash(filename):
    hash_sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


class Album(models.Model):
    parent_album = models.PositiveIntegerField(_('Parent album'), null=True, blank=True)
    title = models.CharField(_('Title'), max_length=255)
    date = models.DateField(_('Date'), auto_now_add=True)
    description = models.TextField(_('Description'), null=True, blank=True)
    directory = models.SlugField(_('Directory'))
    album_cover = models.CharField(_('Album cover'), max_length=255)
    sort_order = models.CharField(_('Sort order'), max_length=255, null=True, blank=True)
    public = models.BooleanField(_('Public'), default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('album')
        verbose_name_plural = _('albums')
        ordering = ('-date',)


class Photo(models.Model):
    def upload_dir(instance, filename):
        return 'photos/%s/%s' % (instance.album.directory, instance.image.name)

    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'))
    date = models.DateTimeField(_('Date'), auto_now_add=True)
    image = models.ImageField(_('Image file'), upload_to=upload_dir)
    description = models.TextField(_('Description'), blank=True)
    file_hash = models.CharField(_('SHA-256'), max_length=255, blank=True)
    preview_img = models.ImageField(_('Preview image'), blank=True)
    hidpi_preview_img = models.ImageField(_('High DPI preview image'), blank=True)
    thumbnail_img = models.ImageField(_('Thumbnail image'), blank=True)
    hidpi_thumbnail_img = models.ImageField(_('High DPI thumbnail image'), blank=True)

    def filename(self):
        return os.path.basename(self.image.name)

    def preview_dir(self):
        preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews', self.album.directory)
        if not os.path.exists(preview_dir):
            os.makedirs(preview_dir)
        return os.path.join(os.path.relpath(preview_dir, start=settings.MEDIA_ROOT))

    def create_preview_image(self):
        if self.image.height > 1170 or self.image.width > 1170:
            with Image(filename=self.image.path) as img:
                img.transform(resize='1170x1170')
                img.compression_quality = 80
                img.save(filename=os.path.join(settings.MEDIA_ROOT, self.preview_dir(), 'preview_' + self.filename()))
                self.preview_img = os.path.join(self.preview_dir(), self.filename())

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Photo, self).save(*args, **kwargs)
        self.file_hash = calc_hash(self.image.path)
        self.create_preview_image()
        super(Photo, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if os.path.isfile(self.image.path):
            os.remove(self.image.path)
        if self.preview_img:
            try:
                os.remove(self.preview_img.path)
            except Exception:
                pass
        super(Photo, self).delete(*args, **kwargs)


    class Meta:
        verbose_name = _('photo')
        verbose_name_plural = _('photos')
        ordering = ('-date',)
