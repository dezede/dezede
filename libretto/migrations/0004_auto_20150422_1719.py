# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0003_migrate_typedensemble'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='caracteristiquedensemble',
            name='caracteristique_ptr',
        ),
        migrations.RemoveField(
            model_name='typedecaracteristiquedensemble',
            name='typedecaracteristique_ptr',
        ),
        migrations.DeleteModel(
            name='TypeDeCaracteristiqueDEnsemble',
        ),
        migrations.RemoveField(
            model_name='ensemble',
            name='caracteristiques',
        ),
        migrations.DeleteModel(
            name='CaracteristiqueDEnsemble',
        ),
        migrations.AlterField(
            model_name='elementdedistribution',
            name='evenement',
            field=models.ForeignKey(related_name='distribution', on_delete=django.db.models.deletion.PROTECT, verbose_name='\xe9v\xe9nement', blank=True, to='libretto.Evenement', null=True),
            preserve_default=True,
        ),
    ]
