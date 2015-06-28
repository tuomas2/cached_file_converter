"""
    Copyright (C) 2015 Tuomas Airaksinen.
    See LICENCE.txt
"""
import time, os
import logging
from django.conf import settings
from django.db import transaction
from django.db.models import Q

logger = logging.getLogger('task_processor')

from django.core.management.base import BaseCommand
from cached_file_converter.models import Task, TASK_STATUSES
from cached_file_converter.utils import get_output_filenames, get_output_filenanes_and_options


class Command(BaseCommand):
    help = "Poll continuously for file conversion tasks and process them"

    def cleanup(self, output_files):
         for output_file in output_files.values():
            if os.path.exists(output_file):
                os.remove(output_file)

    def handle(self, *args, **options):
        logger.info('Processing tasks forever')
        try:
            while True:
                time.sleep(getattr(settings, 'TASK_PROSESSOR_SLEEP', 1))
                with transaction.atomic():
                    task = Task.objects.filter(
                        Q(status=TASK_STATUSES.index('finished'), converter_revision__lt=settings.CONVERTER_REVISION) |
                        Q(status=TASK_STATUSES.index('waiting'))).order_by('status', 'created_at').first()
                    if not task:
                        continue
                    print 'but now:', task
                    input_file = os.path.join(settings.ORIGINAL_FILES, '%s.dat'%task.md5)
                    output_files = get_output_filenames(task.md5)

                    self.cleanup(output_files)

                    task.status = TASK_STATUSES.index('ongoing')
                    task.save()
                try:
                    logger.info('Started processing %s %s', task.orig_filename, task.md5)
                    settings.CONVERTER_FUNC(input_file, get_output_filenanes_and_options(task.md5), task)
                    logger.info('Finished %s', task.md5)
                    task.converter_revision = settings.CONVERTER_REVISION
                    task.status = TASK_STATUSES.index('finished')
                except KeyboardInterrupt:
                    logger.info('Keyboard interrupt - stopping now! %s', task.md5)
                    self.cleanup(output_files)
                    task.status = TASK_STATUSES.index('waiting')
                    task.save()
                    raise
                except Exception as e:
                    self.cleanup(output_files)
                    task.status = TASK_STATUSES.index('error')
                    logger.error('Error while processing %s: %s',task.md5, e)
                print 'task now: ', task
                task.save()
                t = Task.objects.get(pk=task.pk)
                print 'and now: ', t

        except KeyboardInterrupt:
            logger.info('Exiting gracefully. Bye!')