# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import dezede.models


class Migration(migrations.Migration):

    dependencies = [
        ('dezede', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diapositive',
            name='position',
            field=models.PositiveSmallIntegerField(default=dezede.models.get_default_position, verbose_name='position'),
            preserve_default=True,
        ),
    ]
