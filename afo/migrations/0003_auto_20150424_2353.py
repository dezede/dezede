# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('afo', '0002_import_from_libretto'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='evenementafo',
            options={'verbose_name': '\xe9v\xe9nement AFO', 'verbose_name_plural': '\xe9v\xe9nements AFO'},
        ),
        migrations.AlterModelOptions(
            name='lieuafo',
            options={'verbose_name': 'lieu ou institution AFO', 'verbose_name_plural': 'lieux et institutions AFO'},
        ),
        migrations.AddField(
            model_name='evenementafo',
            name='modalite_de_production',
            field=models.CharField(blank=True, max_length=2, verbose_name='modalit\xe9 de production', choices=[('P', 'participation aux frais'), ('A', 'autoproduction'), ('Ce', 'contrat de cession'), ('Cp', 'contrat de coproduction'), ('Cr', 'contrat de cor\xe9alisation')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='evenementafo',
            name='nom_festival',
            field=models.CharField(max_length=80, verbose_name='nom du festival', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='evenementafo',
            name='nomenclature',
            field=models.TextField(verbose_name='nomenclature', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='evenementafo',
            name='permanents',
            field=models.PositiveIntegerField(null=True, verbose_name='nombre de musiciens permanents convoqu\xe9s (dont rempla\xe7ants)', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='evenementafo',
            name='presentation_specifique',
            field=models.CharField(blank=True, max_length=1, verbose_name='pr\xe9sentation sp\xe9cifique', choices=[('C', 'concert comment\xe9 / pr\xe9sent\xe9'), ('P', 'concert participatif'), ('A', 'autre')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='evenementafo',
            name='public_specifique',
            field=models.CharField(blank=True, max_length=2, verbose_name='public sp\xe9cifique', choices=[('P', 'puplic de proximit\xe9'), ('E', 'public emp\xeach\xe9 (sant\xe9, handicap, justice)'), ('S', 'seniors'), ('J', 'jeunes'), ('JS', 'jeunes en temps scolaire'), ('JV', 'jeunes hors temps scolaire')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='evenementafo',
            name='supplementaires',
            field=models.PositiveIntegerField(null=True, verbose_name='nombre de musiciens suppl\xe9mentaires convoqu\xe9s', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='evenementafo',
            name='titre_programme',
            field=models.CharField(max_length=200, verbose_name='titre du programme', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='evenementafo',
            name='tournee',
            field=models.CharField(max_length=60, verbose_name='code ou titre de la tourn\xe9e', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='evenementafo',
            name='type_de_programme',
            field=models.CharField(blank=True, max_length=2, verbose_name='typologie artistique du programme', choices=[('LS', 'lyrique version sc\xe9nique'), ('MC', 'musique de chambre'), ('LC', 'lyrique version concert'), ('S', 'symphonique (dont ch\u0153ur / r\xe9cital)'), ('C', 'chor\xe9graphique'), ('A', 'autre')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lieuafo',
            name='type_de_salle',
            field=models.CharField(blank=True, max_length=1, verbose_name='type_de_salle', choices=[('M', 'd\xe9di\xe9e \xe0 la musique'), ('P', 'pluridisciplinaire'), ('A', 'autre')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evenementafo',
            name='code_programme',
            field=models.CharField(max_length=60, verbose_name='code du programme', blank=True),
            preserve_default=True,
        ),
    ]
