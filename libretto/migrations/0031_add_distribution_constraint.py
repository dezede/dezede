# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0030_auto_20150626_1634'),
    ]

    operations = [
        migrations.RunSQL("""
            DELETE FROM libretto_elementdedistribution
            WHERE individu_id IS NULL AND ensemble_id IS NULL;
            ALTER TABLE libretto_elementdedistribution
            ADD CONSTRAINT individu_xor_ensemble
            CHECK (individu_id IS NOT NULL <> ensemble_id IS NOT NULL);
        """, """
            ALTER TABLE libretto_elementdedistribution
            DROP CONSTRAINT individu_xor_ensemble;
        """)
    ]
