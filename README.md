=====
Simple cached file converter service (Django 1.8 app)
=====

1. Check MD5 sum of a file on client side to avoid waste of bandwith
2. Is file cached on server?
  1. Yes
    1. If file is cached, get immediately a download link for cached converted file
  2. No
    1. Upload file for conversion
    2. Convert file on server (separate task processor)
    3. Get a link for user to download converted file

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
    # set up / import your converter function here.
    def convert(input_file, output_file, task):
        pass
    CONVERTER_FUNC = convert

    # what do you want converted filename to be?
    def get_download_filename(orig_filename):
        return orig_filename.rsplit('.', 1)[0] + '.zip'

    GET_DOWNLOAD_FILENAME = get_download_filename


2. Include the polls URLconf in your project urls.py like this:

    url(r'^cached_file_converter/', include('cached_file_converter.urls')),

3. Run `python manage.py migrate` to create the polls models.

4. Start development server
    python manage.py runserver

and start task prosessor

    python manage.py process_tasks

    and visit http://127.0.0.1:8000/cached_file_converter/.
