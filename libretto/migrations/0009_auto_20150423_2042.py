# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('afo', '0003_auto_20150423_2042'),
        ('dossiers', '0001_initial'),
        ('libretto', '0008_migrate_institutions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='institution',
            name='lieu_ptr',
        ),
        migrations.DeleteModel(
            name='Institution',
        ),
        migrations.RemoveField(
            model_name='lieudivers',
            name='lieu_ptr',
        ),
        migrations.DeleteModel(
            name='LieuDivers',
        ),
        migrations.RemoveField(
            model_name='lieu',
            name='polymorphic_ctype',
        ),
    ]
