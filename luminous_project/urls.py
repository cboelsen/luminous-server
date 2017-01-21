"""luminous_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from openapi_codec import OpenAPICodec

from rest_framework import renderers
from rest_framework.schemas import get_schema_view
from rest_framework.authtoken import views as auth_views

from luminous_photos import views


class SwaggerRenderer(renderers.BaseRenderer):

    media_type = 'application/openapi+json'
    format = 'swagger'

    def render(self, data, media_type=None, renderer_context=None):
        codec = OpenAPICodec()
        return codec.dump(data)


swagger_view = get_schema_view(
    title='Photo Management API',
    renderer_classes=[
        SwaggerRenderer,
    ],
)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', swagger_view),
    url(r'^v1/', include(views.router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', auth_views.obtain_auth_token)
]

urlpatterns += staticfiles_urlpatterns()
