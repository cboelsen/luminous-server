from django.db import models
import uuid


class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=255)
    path = models.CharField(max_length=1024, unique=True)
    album = models.CharField(max_length=255)
    rating = models.PositiveSmallIntegerField(default=50)
    landscape_orientation = models.NullBooleanField()

    def __str__(self):
        return '{}(path="{}")'.format(self.__class__.__name__, self.path)
