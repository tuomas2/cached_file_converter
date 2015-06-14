# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cached_file_converter', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='converter_revision',
            field=models.IntegerField(default=0),
        ),
    ]
