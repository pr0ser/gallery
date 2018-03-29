from celery import shared_task
from django.utils.translation import ugettext_lazy as _

import gallery.models


@shared_task
def post_process_image(photo_id):
    image = gallery.models.Photo.objects.get(id=photo_id)
    image.create_thumbnails()
    image.create_previews()
    image.save_exif_data()
    image.ready = True
    image.save()
    return image.image.path


@shared_task(bind=True)
def async_save_photo(self, album_id):
    photos = gallery.models.Photo.objects.filter(album_id=album_id).iterator()
    album = gallery.models.Album.objects.get(pk=album_id)
    total_count = gallery.models.Photo.objects.filter(album_id=album_id).count()
    for index, photo in enumerate(photos):
        photo.save()
        if not self.request.called_directly:
            self.update_state(
                state='PROGRESS',
                meta={
                    'album': album.directory,
                    'current': index,
                    'total': total_count
                }
            )
    return _('Updated %(total)s photos (%(album)s)') % {
        'album': album.title,
        'total': total_count
    }


@shared_task
def update_album_localities(album_id):
    photos = (gallery.models.Photo.objects.all().filter(album_id=album_id).iterator())
    for photo in photos:
        if hasattr(photo, 'exifdata'):
            photo.exifdata.update_geocoding(overwrite=True)
