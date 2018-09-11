import piexif

from collections import namedtuple
from datetime import datetime

# from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.encoding import get_system_encoding

from ...models import Photo


ExifTags = namedtuple('ExifTags', ['rating', 'date', 'width', 'height'])


def extract_exif_from_photo(path: str):
    tags = {
        'rating': ('0th', piexif.ImageIFD.Rating),
        'width': ('Exif', piexif.ExifIFD.PixelXDimension),
        'height': ('Exif', piexif.ExifIFD.PixelYDimension),
        'date': ('Exif', piexif.ExifIFD.DateTimeOriginal),
    }
    info = {}
    try:
        exif_dict = piexif.load(path)
    except ValueError:
        exif_dict = {}
    for tag_name, tag_id in tags.items():
        try:
            value = exif_dict[tag_id[0]][tag_id[1]]
        except KeyError:
            value = None
        info[tag_name] = value
    if info['date']:
        try:
            date_string = info['date'].decode(get_system_encoding())
            date_unaware = datetime.strptime(date_string, '%Y:%m:%d %H:%M:%S')
            info['date'] = timezone.make_aware(date_unaware, timezone.get_current_timezone())
        except ValueError:
            info['date'] = None
    return ExifTags(info['rating'], info['date'], info['width'], info['height'])


def update_photo_from_exif(photo: Photo):
    exif = extract_exif_from_photo(photo.path)
    need_to_save = False
    if photo.rating != exif.rating and exif.rating != 50 and exif.rating is not None:
        photo.rating = exif.rating
        need_to_save = True
    if exif.width is not None and exif.height is not None:
        landscape_orientation = (exif.width > exif.height)
        if landscape_orientation != photo.landscape_orientation:
            photo.landscape_orientation = landscape_orientation
            need_to_save = True
    if exif.date is not None and exif.date != photo.date:
        photo.date = exif.date
        need_to_save = True
    if need_to_save:
        photo.save()


def extract_photo_info_from_exif():
    filters_list = [
        {'date__isnull': True},
        {'landscape_orientation__isnull': True},
    ]
    for filters in filters_list:
        for photo in Photo.objects.filter(**filters):
            update_photo_from_exif(photo)


class Command(BaseCommand):
    help = 'Find and add new photos, and remove non-existent photos'

    def handle(self, *args, **options):
        extract_photo_info_from_exif()
