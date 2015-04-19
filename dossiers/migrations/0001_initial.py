# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import mptt.fields
import django.db.models.deletion
from django.conf import settings
import libretto.models.base


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libretto', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategorieDeDossiers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(max_length=75)),
                ('position', models.PositiveSmallIntegerField(default=1)),
                ('etat', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=libretto.models.base._get_default_etat, verbose_name='\xe9tat', to='libretto.Etat')),
                ('owner', models.ForeignKey(related_name='categoriededossiers', on_delete=django.db.models.deletion.PROTECT, verbose_name='propri\xe9taire', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('position',),
                'verbose_name': 'cat\xe9gorie de dossiers',
                'verbose_name_plural': 'cat\xe9gories de dossiers',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DossierDEvenements',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titre', models.CharField(max_length=100, verbose_name='titre')),
                ('titre_court', models.CharField(help_text='Utilis\xe9 pour le chemin de fer.', max_length=100, verbose_name='titre court', blank=True)),
                ('position', models.PositiveSmallIntegerField(default=1, verbose_name='position')),
                ('slug', models.SlugField(unique=True)),
                ('date_publication', models.DateField(default=datetime.datetime.now, verbose_name='date de publication')),
                ('publications', models.TextField(verbose_name='publication(s) associ\xe9e(s)', blank=True)),
                ('developpements', models.TextField(verbose_name='d\xe9veloppements envisag\xe9s', blank=True)),
                ('presentation', models.TextField(verbose_name='pr\xe9sentation')),
                ('contexte', models.TextField(verbose_name='contexte historique', blank=True)),
                ('sources_et_protocole', models.TextField(verbose_name='sources et protocole', blank=True)),
                ('bibliographie', models.TextField(verbose_name='bibliographie indicative', blank=True)),
                ('debut', models.DateField(null=True, verbose_name='d\xe9but', blank=True)),
                ('fin', models.DateField(null=True, verbose_name='fin', blank=True)),
                ('circonstance', models.CharField(max_length=100, verbose_name='circonstance', blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('auteurs', models.ManyToManyField(related_name='dossiers', null=True, verbose_name='authors', to='libretto.Individu', blank=True)),
                ('categorie', models.ForeignKey(related_name='dossiersdevenements', blank=True, to='dossiers.CategorieDeDossiers', help_text='Attention, un dossier contenu dans un autre dossier ne peut \xeatre dans une cat\xe9gorie.', null=True, verbose_name='cat\xe9gorie')),
                ('editeurs_scientifiques', models.ManyToManyField(related_name='dossiers_d_evenements_edites', verbose_name='\xe9diteurs scientifiques', to=settings.AUTH_USER_MODEL)),
                ('ensembles', models.ManyToManyField(related_name='dossiers', null=True, verbose_name='ensembles', to='libretto.Ensemble', blank=True)),
                ('etat', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=libretto.models.base._get_default_etat, verbose_name='\xe9tat', to='libretto.Etat')),
                ('evenements', models.ManyToManyField(related_name='dossiers', null=True, verbose_name='events', to='libretto.Evenement', blank=True)),
                ('lieux', models.ManyToManyField(related_name='dossiers', null=True, verbose_name='lieux', to='libretto.Lieu', blank=True)),
                ('oeuvres', models.ManyToManyField(related_name='dossiers', null=True, verbose_name='\u0153uvres', to='libretto.Oeuvre', blank=True)),
                ('owner', models.ForeignKey(related_name='dossierdevenements', on_delete=django.db.models.deletion.PROTECT, verbose_name='propri\xe9taire', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='parent', blank=True, to='dossiers.DossierDEvenements', null=True)),
                ('sources', models.ManyToManyField(related_name='dossiers', null=True, verbose_name='sources', to='libretto.Source', blank=True)),
            ],
            options={
                'ordering': ('tree_id', 'lft'),
                'verbose_name': 'dossier d\u2019\xe9v\xe9nements',
                'verbose_name_plural': 'dossiers d\u2019\xe9v\xe9nements',
                'permissions': (('can_change_status', 'Peut changer l\u2019\xe9tat'),),
            },
            bases=(models.Model,),
        ),
    ]
