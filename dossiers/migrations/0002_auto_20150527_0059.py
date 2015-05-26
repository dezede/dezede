# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0028_auto_20150526_0012'),
        ('dossiers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dossierdevenements',
            name='saisons',
            field=models.ManyToManyField(related_name='saisons', verbose_name='saisons', to='libretto.Saison', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dossierdevenements',
            name='auteurs',
            field=models.ManyToManyField(related_name='dossiers', verbose_name='authors', to='libretto.Individu', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dossierdevenements',
            name='ensembles',
            field=models.ManyToManyField(related_name='dossiers', verbose_name='ensembles', to='libretto.Ensemble', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dossierdevenements',
            name='evenements',
            field=models.ManyToManyField(related_name='dossiers', verbose_name='events', to='libretto.Evenement', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dossierdevenements',
            name='lieux',
            field=models.ManyToManyField(related_name='dossiers', verbose_name='lieux', to='libretto.Lieu', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dossierdevenements',
            name='oeuvres',
            field=models.ManyToManyField(related_name='dossiers', verbose_name='\u0153uvres', to='libretto.Oeuvre', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dossierdevenements',
            name='sources',
            field=models.ManyToManyField(related_name='dossiers', verbose_name='sources', to='libretto.Source', blank=True),
            preserve_default=True,
        ),
    ]
