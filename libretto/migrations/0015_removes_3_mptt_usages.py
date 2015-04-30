# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0014_removes_polymorphic_caracteristics'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='oeuvre',
            options={'ordering': ('type_extrait', 'numero_extrait', 'titre', 'genre', 'numero', 'coupe', 'incipit', 'tempo', 'tonalite', 'sujet', 'arrangement', 'surnom', 'nom_courant', 'opus', 'ict'), 'verbose_name': '\u0153uvre', 'verbose_name_plural': '\u0153uvres', 'permissions': (('can_change_status', 'Peut changer l\u2019\xe9tat'),)},
        ),
        migrations.RemoveField(
            model_name='partie',
            name='level',
        ),
        migrations.RemoveField(
            model_name='partie',
            name='lft',
        ),
        migrations.RemoveField(
            model_name='partie',
            name='rght',
        ),
        migrations.RemoveField(
            model_name='partie',
            name='tree_id',
        ),
        migrations.RemoveField(
            model_name='profession',
            name='level',
        ),
        migrations.RemoveField(
            model_name='profession',
            name='lft',
        ),
        migrations.RemoveField(
            model_name='profession',
            name='rght',
        ),
        migrations.RemoveField(
            model_name='profession',
            name='tree_id',
        ),
        migrations.RemoveField(
            model_name='typedensemble',
            name='level',
        ),
        migrations.RemoveField(
            model_name='typedensemble',
            name='lft',
        ),
        migrations.RemoveField(
            model_name='typedensemble',
            name='rght',
        ),
        migrations.RemoveField(
            model_name='typedensemble',
            name='tree_id',
        ),
        migrations.AlterField(
            model_name='partie',
            name='parent',
            field=models.ForeignKey(related_name='enfant', verbose_name='r\xf4le ou instrument parent', blank=True, to='libretto.Partie', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='profession',
            name='parent',
            field=models.ForeignKey(related_name='enfants', verbose_name='parent', blank=True, to='libretto.Profession', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='typedensemble',
            name='parent',
            field=models.ForeignKey(related_name='enfants', verbose_name='parent', blank=True, to='libretto.TypeDEnsemble', null=True),
            preserve_default=True,
        ),
    ]
