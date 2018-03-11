from background_task import background

import gallery.models


@background
def post_process_image(photo_id):
    image = gallery.models.Photo.objects.get(id=photo_id)
    image.create_thumbnails()
    image.create_previews()
    image.save_exif_data()
    image.ready = True
    image.save()


@background
def async_save_photo(photo_id):
    photo = gallery.models.Photo.objects.get(pk=photo_id)
    photo.save_exif_data()
    photo.save()


@background
def update_album_localities(album_id):
    photos = (gallery.models.Photo.objects.all().filter(album_id=album_id).iterator())
    for photo in photos:
        if hasattr(photo, 'exifdata'):
            photo.exifdata.update_geocoding(overwrite=True)
