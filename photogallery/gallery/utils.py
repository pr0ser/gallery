import hashlib

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
