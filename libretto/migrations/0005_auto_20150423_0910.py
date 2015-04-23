# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0004_auto_20150422_1719'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evenement',
            name='code_programme',
        ),
        migrations.RemoveField(
            model_name='evenement',
            name='exoneres',
        ),
        migrations.RemoveField(
            model_name='evenement',
            name='frequentation',
        ),
        migrations.RemoveField(
            model_name='evenement',
            name='jauge',
        ),
        migrations.RemoveField(
            model_name='evenement',
            name='payantes',
        ),
        migrations.RemoveField(
            model_name='evenement',
            name='scolaires',
        ),
        migrations.RemoveField(
            model_name='lieu',
            name='code_postal',
        ),
        migrations.RemoveField(
            model_name='lieu',
            name='type_de_scene',
        ),
    ]
