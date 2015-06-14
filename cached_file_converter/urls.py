"""
    Copyright (C) 2015 Tuomas Airaksinen.
    See LICENCE.txt
"""

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.startpage, name='index'),
    url(r'^is_file_cached$', views.is_file_cached, name='is_file_cached'),
    url(r'^upload$', views.upload, name='upload'),
    url(r'^download/(.*)$', views.download, name='download'),
]