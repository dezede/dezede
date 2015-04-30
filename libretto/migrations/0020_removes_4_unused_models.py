# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0019_pupitre_facultatif'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='devise',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='engagement',
            name='devise',
        ),
        migrations.DeleteModel(
            name='Devise',
        ),
        migrations.RemoveField(
            model_name='engagement',
            name='individus',
        ),
        migrations.RemoveField(
            model_name='engagement',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='engagement',
            name='profession',
        ),
        migrations.RemoveField(
            model_name='personnel',
            name='engagements',
        ),
        migrations.DeleteModel(
            name='Engagement',
        ),
        migrations.RemoveField(
            model_name='personnel',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='personnel',
            name='saison',
        ),
        migrations.RemoveField(
            model_name='personnel',
            name='type',
        ),
        migrations.RemoveField(
            model_name='typedepersonnel',
            name='owner',
        ),
        migrations.DeleteModel(
            name='TypeDePersonnel',
        ),
        migrations.RemoveField(
            model_name='elementdeprogramme',
            name='personnels',
        ),
        migrations.DeleteModel(
            name='Personnel',
        ),
    ]
