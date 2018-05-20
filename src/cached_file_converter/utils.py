"""
    Copyright (C) 2015 Tuomas Airaksinen.
    See LICENCE.txt
"""

import math
import os
from django.conf import settings
from django.urls import reverse


def get_output_filenanes_and_options(md5):
    return {name: (os.path.join(settings.CONVERTED_FILES, '%s_%s.dat'%(md5, name.lower().replace(' ', '_'))), options)
           for name, options in settings.CONVERTER_OPTIONS.items()}

def get_output_filenames(md5):
    return {k:v[0] for k, v in get_output_filenanes_and_options(md5).items()}


def get_download_links(filename, md5):
    def convert_size(size):
        size /= 1024.
        size_name = ("kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size,1024)))
        p = math.pow(1024,i)
        s = round(size/p,2)
        if (s > 0):
            return '%s %s' % (s,size_name[i])
        else:
            return '0B'

    return {name: {'url': reverse('cached:download', args=(name.replace(' ', '_').lower(), filename)),
                   'size': convert_size(os.path.getsize(get_converted_filename(md5, name)))}
            for name in list(settings.CONVERTER_OPTIONS.keys())
            }


def get_converted_filename(md5, version_name):
    return os.path.join(settings.CONVERTED_FILES, '%s_%s.dat' % (md5, version_name.replace(' ', '_').lower()))