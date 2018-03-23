# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('afo', '0006_auto_20150507_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evenementafo',
            name='modalite_de_production',
            field=models.CharField(verbose_name='modalité de production', max_length=2, blank=True, choices=[('P', 'participation aux frais'), ('A', 'autoproduction'), ('Ce', 'contrat de cession'), ('Cp', 'contrat de coproduction'), ('Cr', 'contrat de coréalisation'), ('L', 'location')]),
        ),
        migrations.AlterField(
            model_name='evenementafo',
            name='presentation_specifique',
            field=models.CharField(verbose_name='présentation spécifique', max_length=1, blank=True, choices=[('C', 'concert commenté/présenté'), ('P', 'concert participatif'), ('A', 'autre')]),
        ),
        migrations.AlterField(
            model_name='evenementafo',
            name='public_specifique',
            field=models.CharField(verbose_name='public spécifique', max_length=2, blank=True, choices=[('P', 'public de proximité'), ('E', 'public empêché (santé, handicap, justice)'), ('S', 'seniors'), ('J', 'jeunes'), ('JS', 'jeunes en temps scolaire'), ('JV', 'jeunes hors temps scolaire')]),
        ),
        migrations.AlterField(
            model_name='evenementafo',
            name='type_de_programme',
            field=models.CharField(verbose_name='typologie artistique du programme', max_length=2, blank=True, choices=[('LS', 'lyrique version scénique'), ('MC', 'musique de chambre'), ('LC', 'lyrique version concert'), ('S', 'symphonique (dont chœur/récital)'), ('C', 'chorégraphique'), ('A', 'autre')]),
        ),
        migrations.AlterField(
            model_name='lieuafo',
            name='type_de_salle',
            field=models.CharField(verbose_name='type de salle', max_length=1, blank=True, choices=[('M', 'dédiée à la musique'), ('P', 'pluridisciplinaire'), ('A', 'autre')]),
        ),
    ]
