# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0033_auto_20160624_2318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='cote',
            field=models.CharField(db_index=True, verbose_name='cote', blank=True, max_length=60),
        ),
        migrations.AlterField(
            model_name='source',
            name='transcription',
            field=tinymce.models.HTMLField(verbose_name='transcription', blank=True, help_text='Recopier la source ou un extrait en suivant les règles définies dans <a href="/examens/source">le didacticiel.</a>'),
        ),
    ]
