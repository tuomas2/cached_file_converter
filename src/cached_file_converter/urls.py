"""
    Copyright (C) 2015 Tuomas Airaksinen.
    See LICENCE.txt
"""

from django.conf.urls import url, include

from . import views

_urlpatterns = [
    url(r'^is_file_cached$', views.is_file_cached, name='is_file_cached'),
    url(r'^upload$', views.upload, name='upload'),
    url(r'^download/(.*)/(.*)$', views.download, name='download'),
    url(r'^queue_length$', views.queue_length, name='queue_length'),
    url(r'^$', views.startpage, name='index'),
]

urlpatterns = [ url(r'', include((_urlpatterns, 'cached_file_converter'), namespace='cached'))]