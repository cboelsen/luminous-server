import apium

from datetime import datetime, timedelta

from luminous_photos.management.commands.update_photos import update_photos
from luminous_photos.management.commands.extract_photo_info_from_exif import extract_photo_info_from_exif


@apium.schedule_task()
@apium.schedule_task(datetime.now().replace(hour=23, minute=45), repeat_every=timedelta(days=1))
def update_photos_daily():
    update_photos()
    extract_photo_info_from_exif()
