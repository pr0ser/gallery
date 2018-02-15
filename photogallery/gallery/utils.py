import hashlib
import json
from os import environ
from urllib import parse, request

from PIL import Image


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


def rev_geocode_lookup(latitude, longitude):
    coordinates = str(latitude) + ',' + str(longitude)
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    params = parse.urlencode(
        {
            'key': environ['GEOCODING_API_KEY'],
            'language': 'fi',
            'result_type': 'locality|administrative_area_level_3|administrative_area_level_2|administrative_area_level_1',
            'latlng': coordinates
        })
    response = None
    address_comps = None

    try:
        response = json.load(request.urlopen(base_url + params))
        address_comps = response['results'][0]['address_components']
    except Exception as e:
        print(f'Error performing reverse geocode lookup: {e}')

    if response['status'] == 'OK':
        return address_comps


def get_locality(geocode_lookup):
    for c in geocode_lookup:
        if 'locality' and 'political' in c['types']:
            return c['long_name']
        if 'administrative_area_level_3' in c['types'] and 'political' in c['types']:
            return c['long_name']
        if 'administrative_area_level_2' in c['types'] and 'political'in c['types']:
            return c['long_name']
        if 'administrative_area_level_1' in c['types'] and 'political' in c['types']:
            return c['long_name']


def get_country(geocode_lookup):
    for c in geocode_lookup:
        if 'country' in c['types'] and 'political' in c['types']:
            return c['long_name']


def get_locality_and_country(latitude, longitude):
    try:
        lookup = rev_geocode_lookup(latitude, longitude)
        locality = get_locality(lookup)
        country = get_country(lookup)
        return locality, country
    except Exception:
        return None
