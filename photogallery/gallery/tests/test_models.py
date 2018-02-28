import datetime
import tempfile
from os import path, chdir

from PIL import Image
from django.test import TestCase
from django.test import override_settings
from django.core.exceptions import ValidationError

from gallery.models import Album, Photo


def get_temporary_image(temp_file, width, height):
    image = Image.new("RGB", (height, width))
    image.save(temp_file, format='JPEG')
    return temp_file


class TestCreateAlbum(TestCase):
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

    def test_album_directory(self):
        self.assertEqual(self.public_album.directory, 'public-album')

    def test_public_albums(self):
        self.assertTrue(self.public_album.public)

    def test_private_albums(self):
        self.assertFalse(self.private_album.public)

    def test_album_creation_date(self):
        date = datetime.datetime.now()
        self.assertEqual(self.public_album.date, date.date())

    def test_album_manual_creation_date(self):
        date = datetime.date(2018, 1, 30)
        self.assertEqual(self.private_album.date, date)

    def test_absolute_url(self):
        self.assertEqual(self.public_album.get_absolute_url(), '/album/public-album')

    def test_album_media_dir(self):
        self.assertEqual(self.public_album.media_dir, 'photos/public-album')

    def test_pending_photos(self):
        self.assertEqual(self.public_album.pending_photos, 0)

    def test_default_sort_order(self):
        self.assertEqual(self.public_album.sort_order, 'title')

    def test_custom_sort_order(self):
        self.assertEqual(self.private_album.sort_order, 'date')

    def test_album_cover_photo(self):
        self.assertIsNone(self.public_album.album_cover)

    def test_description(self):
        self.assertEqual(self.public_album.description, 'Test description.')

    def test_title_validator(self):
        album = Album.objects.create(title='new')
        self.assertRaises(ValidationError, album.full_clean)


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
