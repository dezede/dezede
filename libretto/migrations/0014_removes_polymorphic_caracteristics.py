# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libretto', '0013_auto_20150425_1207'),
    ]

    operations = [
        # Migration écrite à la main
        migrations.AlterField('Evenement', 'caracteristiques',
                              models.ManyToManyField('Caracteristique', related_name='evenements', blank=True, null=True, verbose_name='caractéristiques')),
        migrations.AlterField('ElementDeProgramme', 'caracteristiques',
                              models.ManyToManyField('Caracteristique', related_name='elements_de_programme', blank=True, null=True, verbose_name='caractéristiques')),
        migrations.DeleteModel('CaracteristiqueDeProgramme'),
        migrations.DeleteModel('TypeDeCaracteristiqueDeProgramme'),
        migrations.RemoveField('Caracteristique', 'polymorphic_ctype'),
        migrations.RemoveField('TypeDeCaracteristique', 'polymorphic_ctype'),
        migrations.RenameModel(old_name='Caracteristique',
                               new_name='CaracteristiqueDeProgramme'),
        migrations.RenameModel(old_name='TypeDeCaracteristique',
                               new_name='TypeDeCaracteristiqueDeProgramme'),
        migrations.AlterUniqueTogether(name='caracteristiquedeprogramme',
                                       unique_together={('type', 'valeur')}),

        # Mise à jour automatique des métadonnées des champs
        migrations.AlterModelOptions(name='caracteristiquedeprogramme', options={'ordering': ('type', 'classement', 'valeur'), 'verbose_name': 'caract\xe9ristique de programme', 'verbose_name_plural': 'caract\xe9ristiques de programme'}),
        migrations.AlterModelOptions(name='typedecaracteristiquedeprogramme', options={'ordering': ('classement',), 'verbose_name': 'type de caract\xe9ristique de programme', 'verbose_name_plural': 'types de caract\xe9ristique de programme'}),
        migrations.AlterField(model_name='caracteristiquedeprogramme', name='owner', field=models.ForeignKey(related_name='caracteristiquedeprogramme', on_delete=django.db.models.deletion.PROTECT, verbose_name='propri\xe9taire', blank=True, to=settings.AUTH_USER_MODEL, null=True), preserve_default=True),
        migrations.AlterField(model_name='typedecaracteristiquedeprogramme', name='owner', field=models.ForeignKey(related_name='typedecaracteristiquedeprogramme', on_delete=django.db.models.deletion.PROTECT, verbose_name='propri\xe9taire', blank=True, to=settings.AUTH_USER_MODEL, null=True), preserve_default=True),
    ]
