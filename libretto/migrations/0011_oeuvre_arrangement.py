# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0010_removes_useless_db_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='oeuvre',
            name='arrangement',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='arrangement', db_index=True, choices=[(1, 'transcription'), (2, 'orchestration')]),
            preserve_default=True,
        ),
    ]
