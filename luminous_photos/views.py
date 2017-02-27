import pathlib
import piexif
import re

from jpegtran import JPEGImage

from django.http import HttpResponse

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import routers, viewsets

from rest_framework.decorators import detail_route
from rest_framework.exceptions import (
    APIException,
    # NotAuthenticated,
    # NotFound,
    ParseError,
    # PermissionDenied,
)
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from .models import (
    Photo,
)
from .serializers import (
    PhotoSerializer,
)


def check_request_data_for(request, required_parameters):
    if not all(p in request.data for p in required_parameters):
        raise ParseError('Request body requires all of: {}'.format(required_parameters))


def all_filters(serializer_class):
    QUERY_TERMS = {
        'exact', 'iexact', 'contains', 'icontains', 'gt', 'gte', 'lt', 'lte',
        'in', 'startswith', 'istartswith', 'endswith', 'iendswith', 'range',
        'isnull', 'search', 'regex', 'iregex',
    }
    fields = serializer_class().get_fields()
    filters = {f: QUERY_TERMS for f in fields if f != 'url'}
    return filters


def proportionally_scale_dimensions(img, size):
    ratio_w, ratio_h = img.width / size[0], img.height / size[1]
    ratio = ratio_w if ratio_w > ratio_h else ratio_h
    new_width = int(img.width // ratio)
    new_height = int(img.height // ratio)
    return (new_width, new_height)


def scale_image_to_fit_size(path, size):
    desired_width, desired_height = size
    img = JPEGImage(path)
    if img.width < desired_width and img.height < desired_height:
        return bytes(img.data)
    downscaled_image = img.downscale(*proportionally_scale_dimensions(img, size), quality=90)
    return bytes(downscaled_image.data)


def write_rating_to_exif(path, rating):
    exif_dict = piexif.load(path)
    exif_dict['0th'][piexif.ImageIFD.Rating] = rating
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, path)


def regenerate_path_from_new_title(photo, new_title):
    current_path = pathlib.Path(photo.path)
    try:
        index = re.match(r'\d{4}\.\d{2}\.\d{2}-(?P<index>\d{3,4}).*\.jpg', current_path.name).group('index')
    except AttributeError:
        index = '0001'
    filename = '{0}-{{}} - {1}.jpg'.format(photo.date.strftime('%Y.%m.%d'), new_title)
    new_path = current_path.parent / filename.format(index)
    for i in range(1, 10000):
        if new_path.exists():
            index = str(i).zfill(4)
            new_path = current_path.parent / filename.format(index)
        else:
            break
    else:
        raise Exception('Could not find a free index from which to generate a filename')
    return str(new_path)


class PhotoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows photos to be viewed or edited.
    """
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = all_filters(PhotoSerializer)
    ordering_fields = ('date', 'path', '?')

    def get_serializer_context(self):
        return {
            'request': None,
            'format': self.format_kwarg,
            'view': self,
        }

    def destroy(self, request, *args, **kwargs):
        raise NotImplementedError('no delete via API')

    def create(self, request, *args, **kwargs):
        raise NotImplementedError('no create via API')

    def update(self, request, *args, **kwargs):
        invalid_fields = ['id', 'date', 'path', 'album', 'landscape_orientation']
        if any(f in request.data for f in invalid_fields):
            raise ParseError(
                "Request body contains fields that can't be directly updated, which are {}".format(invalid_fields)
            )

        photo = self.get_object()

        if 'rating' in request.data:
            rating = int(request.data['rating'])
            if rating != photo.rating:
                assert 0 <= rating <= 100
                write_rating_to_exif(photo.path, rating)

        if 'title' in request.data:
            title = request.data['title']
            if title != photo.title:
                current_path = pathlib.Path(photo.path)
                new_path = regenerate_path_from_new_title(photo, title)
                photo.path = new_path
                photo.save()
                current_path.rename(new_path)

        return super().update(request, *args, **kwargs)

    @detail_route(methods=['get'])
    def image(self, request, pk=None):
        max_dimension = 3840
        params = self.request.query_params.dict()
        width = int(params.get('width', 0))
        height = int(params.get('height', 0))

        photo = Photo.objects.get(id=pk)

        if width and height:
            if width > max_dimension or height > max_dimension:
                raise APIException(
                    'Requested image size cannot be greater than 4K resolution',
                    'The maximum requested image size must be less than {} '
                    'pixels in width and height.'.format(max_dimension)
                )
            image_data = scale_image_to_fit_size(photo.path, (width, height))
        else:
            image_data = open(photo.path, 'rb').read()
        return HttpResponse(image_data, content_type='image/jpeg')

    @detail_route(methods=['put', 'patch'])
    def rotate(self, request, pk=None):
        check_request_data_for(request, ['rotation'])
        rotation = int(request.data['rotation'])
        acceptable_rotations = [90, 180, 270]
        if rotation not in acceptable_rotations:
            raise ParseError('Can only rotate by 90 or 270 degrees.')

        photo = Photo.objects.get(id=pk)
        img = JPEGImage(photo.path)
        img = img.rotate(rotation)
        img.save(photo.path)

        photo.landscape_orientation = (img.width > img.height)
        photo.save()
        return Response(PhotoSerializer(photo, context={'request': None}).data)


router = routers.DefaultRouter()
router.register(r'photos', PhotoViewSet)
