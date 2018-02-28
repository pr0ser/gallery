import datetime
import tempfile
from os import path, chdir

from PIL import Image
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import override_settings

from gallery.models import Album, Photo


def get_temporary_image(temp_file, width, height):
    image = Image.new("RGB", (width, height))
    image.save(temp_file, format='JPEG')
    return temp_file


class TestNewAlbum(TestCase):
    def setUp(self):

        self.public_album = Album.objects.create(
            title='Public Album',
            description='Test description.'
        )
        self.private_album = Album.objects.create(
            title='Private Album',
            public=False,
            date=datetime.date(2018, 1, 30),
            sort_order='date'
        )

    def test_directory(self):
        self.assertEqual(self.public_album.directory, 'public-album')

    def test_public_album(self):
        self.assertTrue(self.public_album.public)

    def test_private_album(self):
        self.assertFalse(self.private_album.public)

    def test_creation_date(self):
        date = datetime.datetime.now()
        self.assertEqual(self.public_album.date, date.date())

    def test_manual_creation_date(self):
        date = datetime.date(2018, 1, 30)
        self.assertEqual(self.private_album.date, date)

    def test_absolute_url(self):
        self.assertEqual(self.public_album.get_absolute_url(), '/album/public-album')

    def test_media_dir(self):
        self.assertEqual(self.public_album.media_dir, 'photos/public-album')

    def test_pending_photos(self):
        self.assertEqual(self.public_album.pending_photos, 0)

    def test_default_sort_order(self):
        self.assertEqual(self.public_album.sort_order, 'title')

    def test_custom_sort_order(self):
        self.assertEqual(self.private_album.sort_order, 'date')

    def test_invalid_sort_order(self):
        album = Album.objects.create(title='Test album', sort_order='id')
        self.assertRaises(ValidationError, album.full_clean)

    def test_cover_photo(self):
        self.assertIsNone(self.public_album.album_cover)

    def test_description(self):
        self.assertEqual(self.public_album.description, 'Test description.')

    def test_title_validator(self):
        album = Album.objects.create(title='new')
        self.assertRaises(ValidationError, album.full_clean)

    def test_default_options(self):
        self.assertFalse(self.public_album.downloadable)
        self.assertTrue(self.public_album.show_metadata)
        self.assertTrue(self.public_album.show_location)


class TestSubAlbum(TestCase):
    def setUp(self):
        self.root_album = Album.objects.create(title='Root album')
        self.sub_album = Album.objects.create(title='Sub album', parent=self.root_album)
        self.sub_sub_album = Album.objects.create(title='Sub sub album', parent=self.sub_album)

    def test_root_album(self):
        self.assertIsNone(self.root_album.parent)

    def test_sub_album(self):
        self.assertEqual(self.sub_album.parent, self.root_album)

    def test_parent_albums(self):
        self.assertEqual(self.sub_album.parent_albums(), [self.root_album])
        self.assertEqual(self.sub_sub_album.parent_albums(), [self.sub_album, self.root_album])


class TestAlbumDelete(TestCase):
    def setUp(self):
        self.album = Album.objects.create(title='Test album')

    def test_album_deletion(self):
        self.album.delete()
        self.assertIsNone(self.album.id)


class TestAlbumEdit(TestCase):
    def setUp(self):
        self.album = Album.objects.create(title='Test album', description='Test description')

    def test_description_change(self):
        self.album.description = 'Changed description'
        self.album.save()
        self.assertEqual(self.album.description, 'Changed description')

    def test_title_change(self):
        old_dir = self.album.directory
        self.album.title = 'Changed title'
        self.album.save()
        self.assertEqual(self.album.directory, old_dir)

    def test_changing_options(self):
        self.album.downloadable = True
        self.album.show_metadata = False
        self.album.show_location = False
        self.album.save()
        self.assertTrue(self.album.downloadable)
        self.assertFalse(self.album.show_metadata)
        self.assertFalse(self.album.show_location)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestNewPhoto(TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            prefix='test-photo',
            suffix='.jpg'
        )
        test_image = get_temporary_image(self.temp_file, width=200, height=100)
        self.test_time = datetime.datetime.now()
        self.album = Album.objects.create(title='Album')
        self.photo = Photo(
            title='Test Photo',
            image=test_image.name,
            album=self.album,
            date=self.test_time
        )
        self.photo.save()

    def test_title(self):
        self.assertEqual(self.photo.title, 'Test Photo')

    def test_slug(self):
        self.assertEqual(self.photo.slug, 'test-photo')

    def test_datetime(self):
        self.assertEqual(self.photo.date.date(), self.test_time.date())

    def test_image_path(self):
        self.assertEqual(self.temp_file.name, self.photo.image.path)

    def test_image_size(self):
        self.assertEqual(self.photo.image.width, 200)
        self.assertEqual(self.photo.image.height, 100)

    def test_image_name(self):
        self.assertEqual(self.photo.image.name, self.temp_file.name)

    def test_ready(self):
        self.assertTrue(self.photo.ready)

    def test_empty_description(self):
        self.assertEqual(self.photo.description, '')

    def test_empty_preview_image(self):
        self.assertFalse(bool(self.photo.preview_img))

    def test_empty_hidpi_preview(self):
        self.assertFalse(bool(self.photo.hidpi_preview_img))

    def test_thumbnail_img(self):
        self.assertTrue(bool(self.photo.thumbnail_img))
        self.assertEqual(self.photo.thumbnail_img.width, 330)
        self.assertEqual(self.photo.thumbnail_img.height, 330)
        self.assertEqual(
            self.photo.thumbnail_img.name,
            path.join(self.photo.preview_dir(), self.photo.thumbnail_img_filename)
        )

    def test_hidpi_thumbnail_img(self):
        self.assertTrue(bool(self.photo.hidpi_thumbnail_img))
        self.assertEqual(self.photo.hidpi_thumbnail_img.width, 600)
        self.assertEqual(self.photo.hidpi_thumbnail_img.height, 600)
        self.assertEqual(
            self.photo.hidpi_thumbnail_img.name,
            path.join(self.photo.preview_dir(), self.photo.hidpi_thumbnail_img_filename)
        )

    def test_get_absolute_url(self):
        self.assertEqual(self.photo.get_absolute_url(), '/photo/test-photo')

    def test_preview_dir(self):
        self.assertEqual(
            self.photo.preview_dir(), path.join('previews', self.photo.album.directory))


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestPhotoFileNames(TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            prefix='test-photo',
            suffix='.jpg'
        )
        test_image = get_temporary_image(self.temp_file, width=100, height=100)
        self.album = Album.objects.create(title='Album')
        self.photo = Photo(
            title='Test Photo',
            image=test_image.name,
            album=self.album,
        )
        self.photo.save()

    def test_preview_filename(self):
        self.assertEqual(
            self.photo.preview_filename,
            'preview_' + path.basename(self.temp_file.name)
        )

    def test_hidpi_preview_filename(self):
        self.assertEqual(
            self.photo.hidpi_preview_filename,
            'hidpipreview_' + path.basename(self.temp_file.name)
        )

    def thumbnail_img_filename(self):
        self.assertEqual(
            self.photo.thumbnail_img_filename,
            'thumb_' + path.basename(self.temp_file.name)
        )

    def hidpi_thumbnail_img_filename(self):
        self.assertEqual(
            self.photo.hidpi_thumbnail_img_filename,
            'hidpithumb_' + path.basename(self.temp_file.name)
        )


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestPhotoPreviewDirCreation(TestCase):
    def setUp(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        test_image = get_temporary_image(temp_file, width=100, height=100)
        self.album = Album.objects.create(title='Album')
        self.photo = Photo(title='Photo', image=test_image.name, album=self.album)
        self.photo.save()

    def test_directory_creation(self):
        chdir(tempfile.gettempdir())
        self.assertTrue(path.isdir(self.photo.preview_dir()))
        self.assertEqual(self.photo.preview_dir(), 'previews/album')

    def test_directory_deletion(self):
        chdir(tempfile.gettempdir())
        preview_dir = self.photo.preview_dir()
        self.assertTrue(path.isdir(preview_dir))
        self.photo.album.delete()
        self.assertFalse(path.isdir(preview_dir))


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestHighResPhoto(TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            prefix='test-photo',
            suffix='.jpg'
        )
        test_image = get_temporary_image(self.temp_file, width=2500, height=2000)
        self.album = Album.objects.create(title='Album')
        self.photo = Photo(
            title='Test Photo',
            image=test_image.name,
            album=self.album,
        )
        self.photo.save()

    def test_preview_image(self):
        image = Image.open(self.photo.preview_img.path)
        self.assertTrue(path.isfile(self.photo.preview_img.path))
        self.assertEqual(self.photo.preview_img.width, 1327)
        self.assertGreater(self.photo.preview_img.width, self.photo.preview_img.height)
        self.assertEqual(image.format, 'JPEG')

    def test_hidpi_preview_image(self):
        image = Image.open(self.photo.hidpi_preview_img.path)
        self.assertTrue(path.isfile(self.photo.hidpi_preview_img.path))
        self.assertEqual(self.photo.hidpi_preview_img.width, 2340)
        self.assertGreater(self.photo.hidpi_preview_img.width, self.photo.hidpi_preview_img.height)
        self.assertEqual(image.format, 'JPEG')


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestMidResPhoto(TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            prefix='test-photo',
            suffix='.jpg'
        )
        test_image = get_temporary_image(self.temp_file, width=1400, height=900)
        self.album = Album.objects.create(title='Album')
        self.photo = Photo(
            title='Test Photo',
            image=test_image.name,
            album=self.album,
        )
        self.photo.save()

    def test_preview_image(self):
        self.assertTrue(path.isfile(self.photo.preview_img.path))
        self.assertEqual(self.photo.preview_img.width, 1327)
        self.assertGreater(self.photo.preview_img.width, self.photo.preview_img.height)
        image = Image.open(self.photo.preview_img.path)
        self.assertEqual(image.format, 'JPEG')

    def test_empty_hidpi_preview_image(self):
        self.assertFalse(bool(self.photo.hidpi_preview_img))


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestLowResPhoto(TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            prefix='test-photo',
            suffix='.jpg'
        )
        test_image = get_temporary_image(self.temp_file, width=800, height=600)
        self.album = Album.objects.create(title='Album')
        self.photo = Photo(
            title='Test Photo',
            image=test_image.name,
            album=self.album,
        )
        self.photo.save()

    def test_empty_preview_image(self):
        self.assertFalse(bool(self.photo.preview_img))

    def test_empty_hidpi_preview_image(self):
        self.assertFalse(bool(self.photo.hidpi_preview_img))

    def test_original_image(self):
        image = Image.open(self.photo.image.path)
        self.assertTrue(bool(self.photo.image))
        self.assertEqual(self.photo.image.width, 800)
        self.assertEqual(self.photo.image.height, 600)
        self.assertEqual(image.format, 'JPEG')


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestNextAndPreviousPhoto(TestCase):
    def setUp(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        test_image = get_temporary_image(temp_file, width=100, height=100)
        self.album = Album.objects.create(title='Album')

        self.photo1 = Photo(title='Photo', image=test_image.name, album=self.album)
        self.photo1.save()

        self.photo2 = Photo(title='Photo 2', image=test_image.name, album=self.album)
        self.photo2.save()

        self.photo3 = Photo(title='Photo 3', image=test_image.name, album=self.album)
        self.photo3.save()

    def test_next(self):
        self.assertIsNotNone(self.photo1.next_photo)
        self.assertEqual(self.photo1.next_photo.id, self.photo2.id)

    def test_not_previous(self):
        self.assertIsNone(self.photo1.previous_photo)

    def test_next_and_prev(self):
        self.assertIsNotNone(self.photo2.next_photo)
        self.assertEqual(self.photo2.next_photo.id, self.photo3.id)

        self.assertIsNotNone(self.photo2.previous_photo)
        self.assertEqual(self.photo2.previous_photo.id, self.photo1.id)

    def test_not_next(self):
        self.assertIsNone(self.photo3.next_photo)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestCustomSortOrderNextAndPrev(TestCase):
    def setUp(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        test_image = get_temporary_image(temp_file, width=100, height=100)
        self.album = Album.objects.create(title='Album', sort_order='-title')

        self.photo1 = Photo(title='Photo', image=test_image.name, album=self.album)
        self.photo1.save()

        self.photo2 = Photo(title='Photo 2', image=test_image.name, album=self.album)
        self.photo2.save()

        self.photo3 = Photo(title='Photo 3', image=test_image.name, album=self.album)
        self.photo3.save()

    def test_next(self):
        self.assertIsNotNone(self.photo3.next_photo)
        self.assertEqual(self.photo3.next_photo.id, self.photo2.id)

    def test_next_and_prev(self):
        self.assertIsNotNone(self.photo2.next_photo)
        self.assertEqual(self.photo2.next_photo.id, self.photo1.id)

        self.assertIsNotNone(self.photo2.previous_photo)
        self.assertEqual(self.photo2.previous_photo.id, self.photo3.id)

    def test_not_next(self):
        self.assertIsNone(self.photo1.next_photo)

    def test_not_previous(self):
        self.assertIsNone(self.photo3.previous_photo)
