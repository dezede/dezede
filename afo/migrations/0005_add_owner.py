# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_owner(apps, schema_editor):
    owner = apps.get_model('accounts', 'Hierarchicuser').objects.get(
        username='afo')
    apps.get_model('afo', 'LieuAFO').objects.update(owner=owner)
    apps.get_model('afo', 'EvenementAFO').objects.update(owner=owner)


def remove_owner(apps, schema_editor):
    apps.get_model('afo', 'LieuAFO').objects.update(owner=None)
    apps.get_model('afo', 'EvenementAFO').objects.update(owner=None)


class Migration(migrations.Migration):

    dependencies = [
        ('afo', '0004_auto_20150430_1721'),
    ]

    operations = [
        migrations.RunPython(add_owner, remove_owner),
    ]
