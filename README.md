=====
Simple cached file converter service
=====

Checks MD5 sum of the file that is to be converted on server and uploads & performs
conversion only if it is not already been converted. If converted file is found
cached on the server, it can be served immediately without upload & conversion.

Quick start
-----------

1. Add "cached_file_converter" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'cached_file_converter',
    )

and set up some settings:

    # the directory where original files will be uploaded
    ORIGINAL_FILES = os.path.join(BASE_DIR, 'original')
    # the directory where converted files will be cached
    CONVERTED_FILES = os.path.join(BASE_DIR, 'converted')
    # increase this if you want all your files converted again
    CONVERTER_REVISION = 0
    # set your converter function here.
    CONVERTER_FUNC = process_task


2. Include the polls URLconf in your project urls.py like this::

    url(r'^cached_file_converter/', include('cached_file_converter.urls')),

3. Run `python manage.py migrate` to create the polls models.

4. Start development server
    python manage.py runserver

and start task prosessor+

    python manage.py process_tasks

    and visit http://127.0.0.1:8000/cached_file_converter/.