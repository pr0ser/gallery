import logging
from datetime import datetime

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from django.conf import settings

log = logging.getLogger(__name__)


class ExifInfo(object):

    def __init__(self, filename):
        self.filename = filename
        self.has_exif_data = False
        self.has_location = False
        self.time_taken = None
        self.make = None
        self.model = None
        self.iso = None
        self.shutter_speed = None
        self.aperture = None
        self.focal_length = None
        self.lens = None
        self.latitude = None
        self.longitude = None
        self.altitude = None

        self.exif_data = self._get_exif_data()
        self._parse_exif_data()

        self.params = [
            self.time_taken,
            self.make,
            self.model,
            self.iso,
            self.shutter_speed,
            self.aperture,
            self.focal_length,
            self.lens
        ]

        if not any(self.params):
            self.has_exif_data = False

        if self.latitude == 0 and self.longitude == 0:
            self.has_location = False

        if any(self.params) and settings.DEBUG:
            log.debug(f'Parsed following EXIF data for file {self.filename}: ')
            for item in self.params:
                log.debug(f'{item}')

    def _get_exif_data(self):
        image = Image.open(self.filename)
        exif_info = image._getexif()
        if exif_info:
            try:
                tags = {}
                for tag, value in exif_info.items():
                    decoded = TAGS.get(tag, tag)
                    if decoded == "GPSInfo":
                        gps_data = {}
                        for t in value:
                            sub_decoded = GPSTAGS.get(t, t)
                            gps_data[sub_decoded] = value[t]
                        tags[decoded] = gps_data
                    else:
                        tags[decoded] = value
                return tags
            except Exception as e:
                log.warning(f'Failed to read EXIF data for file {self.filename}: {e}')
                return None
        else:
            return None

    def _parse_exif_data(self):
        if self.exif_data:
            self.has_exif_data = True
            try:
                self._parse_make()
                self._parse_model()
                self._parse_shutter_speed()
                self._parse_aperture()
                self._parse_focal_length()
                self._parse_iso()
                self._parse_time_taken()
                self._parse_lens()
                self._parse_location()
            except Exception as e:
                log.error(f'Failed to parse EXIF data for file {self.filename}: {e}')

    def _parse_make(self):
        if 'Make' in self.exif_data:
            make = str(self.exif_data['Make']).title().strip()
            self.make = make

    def _parse_model(self):
        if 'Model' in self.exif_data:
            self.model = self.exif_data['Model']

    def _parse_shutter_speed(self):
        if 'ExposureTime' in self.exif_data:
            exposure_values = self.exif_data['ExposureTime']
            if exposure_values[0] < exposure_values[1]:
                if exposure_values[0] / exposure_values[1] >= 0.3:
                    self.shutter_speed = round(exposure_values[0] / exposure_values[1], 1)
                else:
                    shutter_speed = round(1 / (exposure_values[0]/exposure_values[1]))
                    self.shutter_speed = '1/' + str(shutter_speed)
            else:
                self.shutter_speed = exposure_values[0]

    def _parse_aperture(self):
        if 'FNumber' in self.exif_data:
            aperture = self.exif_data['FNumber']
            self.aperture = aperture[0] / aperture[1]

    def _parse_iso(self):
        if 'ISOSpeedRatings' in self.exif_data:
            self.iso = self.exif_data['ISOSpeedRatings']

    def _parse_focal_length(self):
        if 'FocalLength' in self.exif_data:
            focal_length = self.exif_data['FocalLength']
            self.focal_length = focal_length[0] / focal_length[1]

    def _parse_lens(self):
        if 'LensModel' in self.exif_data:
            self.lens = self.exif_data['LensModel']

    def _parse_time_taken(self):
        if 'DateTime' in self.exif_data:
            time_taken = self.exif_data['DateTime']
            parsed_date = datetime.strptime(time_taken, '%Y:%m:%d %H:%M:%S')
            self.time_taken = parsed_date

        if 'DateTimeOriginal' in self.exif_data:
            time_taken = self.exif_data['DateTimeOriginal']
            parsed_date = datetime.strptime(time_taken, '%Y:%m:%d %H:%M:%S')
            self.time_taken = parsed_date

    def _parse_location(self):
        if 'GPSInfo' in self.exif_data:
            gps_info = self.exif_data['GPSInfo']

            if 'GPSLatitude' and 'GPSLatitudeRef' and 'GPSLongitude' and 'GPSLongitudeRef' in gps_info:
                self.latitude = ExifInfo.convert_to_degrees(gps_info['GPSLatitude'])
                if gps_info['GPSLatitudeRef'] != "N":
                    self.latitude = 0 - self.latitude

                self.longitude = ExifInfo.convert_to_degrees(gps_info['GPSLongitude'])
                if gps_info['GPSLongitudeRef'] != "E":
                    self.longitude = 0 - self.longitude

                if 'GPSAltitude' in gps_info:
                    self.altitude = (
                            self.exif_data['GPSInfo']['GPSAltitude'][0] /
                            self.exif_data['GPSInfo']['GPSAltitude'][1])
                self.has_location = True

    @staticmethod
    def convert_to_degrees(value):
        d0 = value[0][0]
        d1 = value[0][1]
        d = float(d0) / float(d1)

        m0 = value[1][0]
        m1 = value[1][1]
        m = float(m0) / float(m1)

        s0 = value[2][0]
        s1 = value[2][1]
        s = float(s0) / float(s1)

        return d + (m / 60.0) + (s / 3600.0)
