# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('md5', models.CharField(max_length=32, serialize=False, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(default=0, db_index=True, choices=[(0, b'waiting'), (1, b'ongoing'), (2, b'finished'), (3, b'error')])),
                ('orig_filename', models.CharField(default=b'no_filename', max_length=64)),
            ],
        ),
    ]
