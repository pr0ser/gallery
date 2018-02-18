import hashlib
import json
import logging
from os import environ
from urllib import parse, request

from PIL import Image

log = logging.getLogger(__name__)


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


def google_geocode_lookup(latitude, longitude):
    coordinates = str(latitude) + ',' + str(longitude)
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    params = parse.urlencode(
        {'key': environ['GEOCODING_API_KEY'],
         'language': 'fi',
         'latlng': coordinates
         }
    )
    response = None
    address_comps = None

    try:
        response = json.load(request.urlopen(base_url + params))
        address_comps = response['results']
    except Exception as e:
        log.error(f'Failed to perform Google Geocoding API lookup '
                  f'for coordinates {latitude},{longitude}: {e}')

    if response['status'] == 'OK':
        return address_comps


def get_locality(geocode_lookup):
    for result in geocode_lookup:
        for c in result['address_components']:
            if 'locality' in c['types'] and 'political' in c['types']:
                return c['long_name']
            if 'administrative_area_level_3' in c['types'] and 'political' in c['types']:
                return c['long_name']
            if 'administrative_area_level_2' in c['types'] and 'political'in c['types']:
                return c['long_name']
            if 'administrative_area_level_1' in c['types'] and 'political' in c['types']:
                return c['long_name']


def get_country(geocode_lookup):
    for result in geocode_lookup:
        for c in result['address_components']:
            if 'country' in c['types'] and 'political' in c['types']:
                return c['long_name']


def get_geocoding(latitude, longitude):
    try:
        lookup = google_geocode_lookup(latitude, longitude)
        locality = get_locality(lookup)
        country = get_country(lookup)
        return locality, country
    except Exception as e:
        log.error(
            f'Failed to parse locality and country information '
            f'for coordinates {latitude},{longitude}: {e}'
        )
        return None
