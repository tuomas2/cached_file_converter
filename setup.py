#!/usr/bin/env python
import setuptools
setuptools.setup(name='cached_file_converter', version='0.0.2',
                 package_dir={"": "src"},
                 packages=setuptools.find_packages('src'),
                 include_package_data=True,
                 zip_safe=False,
                 )
