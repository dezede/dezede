# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0004_auto_20150422_1719'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvenementAFO',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code_programme', models.CharField(max_length=55, verbose_name='code du programme', blank=True)),
                ('exonerees', models.PositiveIntegerField(null=True, verbose_name='entr\xe9es exon\xe9r\xe9es', blank=True)),
                ('payantes', models.PositiveIntegerField(null=True, verbose_name='entr\xe9es payantes', blank=True)),
                ('scolaires', models.PositiveIntegerField(null=True, verbose_name='entr\xe9es scolaires', blank=True)),
                ('frequentation', models.PositiveIntegerField(null=True, verbose_name='fr\xe9quentation totale', blank=True)),
                ('jauge', models.PositiveIntegerField(null=True, verbose_name='jauge', blank=True)),
                ('evenement', models.OneToOneField(related_name='afo', verbose_name='\xe9v\xe9nement', to='libretto.Evenement')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LieuAFO',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code_postal', models.CharField(max_length=10, verbose_name='code postal', blank=True)),
                ('type_de_scene', models.CharField(blank=True, max_length=1, verbose_name='type de sc\xe8ne', choices=[('N', 'nationale'), ('C', 'conventionn\xe9e')])),
                ('lieu', models.OneToOneField(related_name='afo', verbose_name='lieu ou institution', to='libretto.Lieu')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
