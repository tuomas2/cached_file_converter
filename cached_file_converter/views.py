import hashlib
import json, os
import time
import logging
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import transaction

logger = logging.getLogger('cached_file_converter')

from django.http import Http404, HttpResponse
from django.shortcuts import render

from .models import Task, TASK_STATUSES

def startpage(request):
    return render(request, 'cached_file_converter/converter_page.html', {'version': '1.0'})

##############
# AJAX views:#
##############

def get_download_filename(orig_filename):
    return orig_filename.rsplit('.', 1)[0] + '.zip'

def is_file_cached(request):
    if request.is_ajax():
        client_md5 = request.POST.get('md5')
        filename = get_download_filename(request.POST.get('filename'))
        rv = {'status': 0}
        if os.path.exists(os.path.join(settings.CONVERTED_FILES, '%s.dat'%client_md5)):
            rv = {'status': 1,'cached': 1, 'download_link': reverse('cached:download', args=(filename,))}
            request.session['md5'] = client_md5
            allow_download = request.session['allow_download'] = request.session.get('allow_download', {})
            allow_download[filename] = client_md5
            request.session.modified = True
        else:
            orig_file_exists = os.path.exists(os.path.join(settings.ORIGINAL_FILES, '%s.dat'% client_md5))
            if not orig_file_exists:
                rv = {'status': 1, 'cached': 0}
            else:
                task = Task.objects.filter(md5=client_md5).first()
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
                raise Exception('MD5 does not match!')
        else:
            server_md5 = client_md5

        filename = get_download_filename(orig_filename)


        rv = {'status': 0}
        if os.path.exists(os.path.join(settings.ORIGINAL_FILES, '%s.dat'%server_md5)):
            try:
                t = Task.objects.get(md5=server_md5)
                if t.status == TASK_STATUSES.index('error'):
                    logger.error('Task in error status')
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
        else:
            raise Exception('Original not found and file was not sent')

        # Let us give task processor some time to process file.
        while True:
            t = Task.objects.get(md5=server_md5)
            if t.status == TASK_STATUSES.index('finished'):
                if not os.path.exists(os.path.join(settings.CONVERTED_FILES, '%s.dat'%server_md5)):
                    t.status = TASK_STATUSES.index('waiting')
                    t.save()
                    continue
                rv = {'status': 1, "download_link": reverse('cached:download', args=(filename,))}
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

def download(request, filename):
    allow_download = request.session.get('allow_download', {})
    if filename in allow_download:
        md5 = allow_download[filename]
        data = open(os.path.join(settings.CONVERTED_FILES, '%s.dat'%md5)).read()
        del allow_download[filename]
        request.session.modified = True
        return HttpResponse(data, content_type='application/gzip')
    raise Http404
