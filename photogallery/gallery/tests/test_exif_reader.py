from datetime import datetime
from os import chdir

from PIL import Image
from django.test import TestCase

from gallery.exif_reader import ExifInfo
from gallery.utils import auto_orient


class TestExifAutoOrient(TestCase):
    @classmethod
    def setUpTestData(cls):
        chdir('/gallery/gallery/tests/testdata')
        cls.portrait_photo = auto_orient(Image.open('test-photo.jpg'))
        cls.landscape_photo = auto_orient(Image.open('test-photo2.jpg'))

    def test_portrait_photo(self):
        self.assertEqual(self.portrait_photo.height, 400)
        self.assertEqual(self.portrait_photo.width, 300)

    def test_landscape_photo(self):
        self.assertEqual(self.landscape_photo.height, 300)
        self.assertEqual(self.landscape_photo.width, 400)


class TestExifParsing(TestCase):
    @classmethod
    def setUpTestData(cls):
        chdir('/gallery/gallery/tests/testdata')
        cls.exifdata = ExifInfo(filename='test-photo.jpg')

    def test_has_exif_data(self):
        self.assertTrue(self.exifdata.has_exif_data)

    def test_date_taken(self):
        self.assertEqual(self.exifdata.time_taken, datetime(2016, 7, 20, 12, 15, 51))

    def test_make(self):
        self.assertEqual(self.exifdata.make, 'Samsung')

    def test_model(self):
        self.assertEqual(self.exifdata.model, 'SM-G930F')

    def test_iso(self):
        self.assertEqual(self.exifdata.iso, 50)

    def test_shutter_speed(self):
        self.assertEqual(self.exifdata.shutter_speed, '1/2352')

    def test_aperture(self):
        self.assertEqual(self.exifdata.aperture, 1.7)

    def test_focal_length(self):
        self.assertEqual(self.exifdata.focal_length, 4.2)

    def test_lens(self):
        self.assertIsNone(self.exifdata.lens)

    def test_has_location(self):
        self.assertTrue(self.exifdata.has_location)

    def test_latitude(self):
        self.assertEqual(round(self.exifdata.latitude, 6), 65.972500)

    def test_longitude(self):
        self.assertEqual(round(self.exifdata.longitude, 6), 29.246944)

    def test_altitude(self):
        self.assertEqual(self.exifdata.altitude, 279)
