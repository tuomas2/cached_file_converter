from django.db import models

TASK_STATUSES = ['waiting', 'ongoing', 'finished', 'error']


class Task(models.Model):
    md5 = models.CharField(max_length=32, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=0, choices=enumerate(TASK_STATUSES), db_index=True)
    orig_filename = models.CharField(max_length=64, default='no_filename')
    converter_revision = models.IntegerField(default=0) # if software has been updated, file needs to be converted again

    def __unicode__(self):
        return '<Task %s %s %s>'%(self.md5, self.orig_filename, TASK_STATUSES[self.status])
