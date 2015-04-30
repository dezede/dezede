# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0022_migrate_parties'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='instrument',
            name='partie_ptr',
        ),
        migrations.RemoveField(
            model_name='role',
            name='oeuvre',
        ),
        migrations.RemoveField(
            model_name='role',
            name='partie_ptr',
        ),
        migrations.DeleteModel(
            name='Role',
        ),
        migrations.RenameField(
            model_name='partie',
            old_name='oeuvre2',
            new_name='oeuvre',
        ),
        migrations.AlterField(
            model_name='membre',
            name='instrument',
            field=models.ForeignKey(related_name='membres', verbose_name='instrument', blank=True, to='libretto.Partie', null=True),
            preserve_default=True,
        ),
        migrations.DeleteModel(
            name='Instrument',
        ),
        migrations.AlterField(
            model_name='partie',
            name='type',
            field=models.PositiveSmallIntegerField(db_index=True, verbose_name='type', choices=[(1, 'instrument'), (2, 'r\xf4le')]),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='partie',
            unique_together=set([('nom', 'parent', 'oeuvre')]),
        ),
        migrations.RemoveField(
            model_name='partie',
            name='polymorphic_ctype',
        ),
        migrations.AlterModelOptions(
            name='partie',
            options={'ordering': ('type', 'classement', 'nom'),
                     'verbose_name': 'r\xf4le ou instrument',
                     'verbose_name_plural': 'r\xf4les et instruments',
                     'permissions': (
                         ('can_change_status', 'Peut changer l\u2019\xe9tat'),)},
        ),
        migrations.AlterField(
            model_name='partie',
            name='parent',
            field=models.ForeignKey(related_name='enfants', verbose_name='r\xf4le ou instrument parent', blank=True, to='libretto.Partie', null=True),
            preserve_default=True,
        ),
    ]
