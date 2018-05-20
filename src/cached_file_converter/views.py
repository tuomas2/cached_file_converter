import hashlib
import json
import os
import time
import logging

from django.conf import settings
from django.db import transaction
from django.http import Http404, HttpResponse

from django.shortcuts import render

from cached_file_converter.utils import get_download_links, get_converted_filename
from .models import Task, TASK_STATUSES

logger = logging.getLogger('cached_file_converter')

def startpage(request):
    return render(request, 'cached_file_converter/converter_page.html', {'revision': settings.CONVERTER_REVISION})

def download(request, version_name, filename):
    exp_time = getattr(settings, 'DOWNLOAD_SESSION_EXPIRY', 1800)
    request.session.set_expiry(exp_time)
    allow_download = request.session.get('allow_download', {})
    if filename in allow_download:
        md5 = allow_download[filename]
        request.session.modified = True
        try:
            data = open(get_converted_filename(md5, version_name), 'rb').read()
        except Exception as e:
            logger.error('Exception in download %s', e)
            raise Http404

        return HttpResponse(data, content_type='application/data')
    raise Http404

def queue_length(request):
    if request.is_ajax():
        t = Task.objects.filter(md5=request.POST.get('md5', '')).first()
        if t:
            count = Task.objects.filter(status=TASK_STATUSES.index('waiting'), created_at__lt=t.created_at,
                                       converter_revision__lte=settings.CONVERTER_REVISION).count()

            return HttpResponse(json.dumps(count+1), content_type='application/json')
    raise Http404

##############
# AJAX views:#
##############

def is_file_cached(request):
    if request.is_ajax():
        client_md5 = request.POST.get('md5')
        filename = settings.GET_DOWNLOAD_FILENAME(request.POST.get('filename'))
        rv = {'status': 0}
        with transaction.atomic():
            task = Task.objects.filter(md5=client_md5).first()
            if (task and task.status == TASK_STATUSES.index('finished')
                    and task.converter_revision >= settings.CONVERTER_REVISION):
                rv = {'status': 1, 'cached': 1, 'download_links': get_download_links(filename, client_md5)}
                request.session['md5'] = client_md5
                allow_download = request.session['allow_download'] = request.session.get('allow_download', {})
                allow_download[filename] = client_md5
                request.session.modified = True
            else:
                orig_file_exists = os.path.exists(os.path.join(settings.ORIGINAL_FILES, '%s.dat' % client_md5))
                if not orig_file_exists:
                    rv = {'status': 1, 'cached': 0}
                else:
                    if task:
                        if task.status in [TASK_STATUSES.index(i) for i in ['waiting', 'ongoing', 'finished']]:
                            rv = {'status': 2, 'cached': 1}
                        elif task.status == TASK_STATUSES.index('error'):
                            rv = {'status': 0}

            return HttpResponse(json.dumps(rv), content_type='application/json')
    raise Http404

def upload(request):
    if request.is_ajax():
        file = request.FILES.get('file')
        orig_filename = request.POST.get('filename')
        client_md5 = request.POST.get('md5')
        data = ''

        if file:
            data = file.read()
            server_md5 = hashlib.md5(data).hexdigest()
            if server_md5 != client_md5:
                logger.critical('MD5 does not match!')
                raise Exception('MD5 does not match!')
        else:
            server_md5 = client_md5

        filename = settings.GET_DOWNLOAD_FILENAME(orig_filename)

        rv = {'status': 0}
        if os.path.exists(os.path.join(settings.ORIGINAL_FILES, '%s.dat'%server_md5)):
            try:
                t = Task.objects.get(md5=server_md5)
                if t.status == TASK_STATUSES.index('error'):
                    logger.info('Task is already in error status')
            except Task.DoesNotExist:
                logger.error('File is already there, but no task. This is an error case!')
        elif file:
            # Save original file
            fo = open(os.path.join(settings.ORIGINAL_FILES, '%s.dat'%server_md5), 'wb')
            fo.write(data)
            fo.close()
            with transaction.atomic():
                t, created = Task.objects.get_or_create(md5=server_md5)
                t.orig_filename=orig_filename
                t.converter_revision = settings.CONVERTER_REVISION
                t.status = TASK_STATUSES.index('waiting')
                t.save()
            return HttpResponse(json.dumps({'status': 2}), content_type='application/json')
        else:
            logger.critical('Original not found and file was not sent')
            raise Exception('Original not found and file was not sent')

        # Let us give task processor some time to process file.
        while True:
            t = Task.objects.get(md5=server_md5)
            if t.status == TASK_STATUSES.index('finished') and t.converter_revision >= settings.CONVERTER_REVISION:
                rv = {'status': 1, "download_links": get_download_links(filename, server_md5)}
                request.session['md5'] = server_md5
                allow_download = request.session['allow_download'] = request.session.get('allow_download', {})
                allow_download[filename] = server_md5
                request.session.modified = True
                break
            elif t.status == TASK_STATUSES.index('error'):
                break
            else:
                time.sleep(getattr(settings, 'UPLOAD_WAIT_SLEEP', 1))

        return HttpResponse(json.dumps(rv), content_type='application/json')
    raise Http404
