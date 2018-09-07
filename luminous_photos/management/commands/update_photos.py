import pathlib
import re

from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import Photo


def get_title_from_path(path: pathlib.Path):
    filename = str(path.stem)
    photo_has_date_prefix = re.compile(r'^\d{4}\.\d{2}\.\d{2}-\d{3,4} - ').match
    if photo_has_date_prefix(filename):
        title = filename.split(' - ', 1)[1]
    else:
        title = filename
    return title


def create_photo_from_path(path: pathlib.Path):
    album = str(path.parent.name)
    title = get_title_from_path(path)
    return Photo(
        path=path,
        title=title,
        album=album,
    )


class Command(BaseCommand):
    help = 'Find and add new photos, and remove non-existent photos'

    def handle(self, *args, **options):
        start_time = datetime.now()

        root_dir = pathlib.Path(settings.PHOTO_ROOT_DIR)
        glob_patterns = ['*.jpg', '*.JPG']
        disk_photos = set(sum([list(root_dir.rglob(g)) for g in glob_patterns], []))
        db_photos = set(map(pathlib.Path, Photo.objects.values_list('path', flat=True)))

        del_photo_paths = db_photos - disk_photos
        if del_photo_paths:
            Photo.objects.filter(path__in=del_photo_paths).delete()

        new_photo_paths = disk_photos - db_photos
        new_photos = (create_photo_from_path(p) for p in new_photo_paths)
        Photo.objects.bulk_create(new_photos)

        self.stdout.write('Found {} new photos and {} deleted photos, in {} seconds'.format(
            len(new_photo_paths),
            len(del_photo_paths),
            (datetime.now() - start_time).seconds,
        ))
