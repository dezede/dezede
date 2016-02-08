# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.postgres.operations import UnaccentExtension
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dezede', '0002_auto_20150419_1816'),
    ]

    operations = [
        UnaccentExtension(),
    ]
