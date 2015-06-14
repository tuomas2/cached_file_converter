=====
Simple cached file converter service
=====

Quick start
-----------

1. Add "cached_file_converter" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'cached_file_converter',
    )

    and set up some settings:

    ORIGINAL_FILES = os.path.join(BASE_DIR, 'original') # the directory where original files will be uploaded
    CONVERTED_FILES = os.path.join(BASE_DIR, 'converted') # the directory where converted files will be cached
    CONVERTER_REVISION = 0 # increase this if you want all your files converted again
    CONVERTER_FUNC = process_task # set your converter function here.

2. Include the polls URLconf in your project urls.py like this::

    url(r'^cached_file_converter/', include('cached_file_converter.urls')),

3. Run `python manage.py migrate` to create the polls models.

4. Start development server
    python manage.py runserver

    and start task prosessor

    python manage.py process_tasks

    and visit http://127.0.0.1:8000/cached_file_converter/.