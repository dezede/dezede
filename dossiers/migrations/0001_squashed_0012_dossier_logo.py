# Generated by Django 3.2.13 on 2024-04-09 15:03

import datetime
import db_search.sql
from django.conf import settings
import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions
import libretto.models.base
import tree.fields
import tree.operations


class Migration(migrations.Migration):

    replaces = [('dossiers', '0001_initial'), ('dossiers', '0002_auto_20150527_0059'), ('dossiers', '0003_mptt_to_tree'), ('dossiers', '0004_auto_20200625_1521'), ('dossiers', '0005_migrate_tree'), ('dossiers', '0006_auto_20230706_2033'), ('dossiers', '0007_add_search_vectors'), ('dossiers', '0008_add_autocomplete_vector'), ('dossiers', '0009_dossier'), ('dossiers', '0010_remove_dossier_old_fields'), ('dossiers', '0011_dossierdoeuvres'), ('dossiers', '0012_dossier_logo')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libretto', '0060_oeuvre_ambitus'),
        ('tree', '0001_initial'),
        ('db_search', '0001_create_search_configurations'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategorieDeDossiers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=75)),
                ('position', models.PositiveSmallIntegerField(default=1)),
                ('etat', models.ForeignKey(default=libretto.models.base._get_default_etat, on_delete=django.db.models.deletion.PROTECT, to='libretto.etat', verbose_name='état')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='categoriededossiers', to=settings.AUTH_USER_MODEL, verbose_name='propriétaire')),
            ],
            options={
                'ordering': ('position',),
                'verbose_name': 'catégorie de dossiers',
                'verbose_name_plural': 'catégories de dossiers',
            },
        ),
        migrations.CreateModel(
            name='DossierDEvenements',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=100, verbose_name='titre')),
                ('titre_court', models.CharField(blank=True, help_text='Utilisé pour le chemin de fer.', max_length=100, verbose_name='titre court')),
                ('position', models.PositiveSmallIntegerField(default=1, verbose_name='position')),
                ('slug', models.SlugField(help_text='Personnaliser l’affichage du titre du dossier dans l’adresse URL.', unique=True)),
                ('date_publication', models.DateField(default=datetime.datetime.now, verbose_name='date de publication')),
                ('publications', models.TextField(blank=True, verbose_name='publication(s) associée(s)')),
                ('developpements', models.TextField(blank=True, verbose_name='développements envisagés')),
                ('presentation', models.TextField(verbose_name='présentation')),
                ('contexte', models.TextField(blank=True, verbose_name='contexte historique')),
                ('sources_et_protocole', models.TextField(blank=True, verbose_name='sources et protocole')),
                ('bibliographie', models.TextField(blank=True, verbose_name='bibliographie indicative')),
                ('debut', models.DateField(blank=True, null=True, verbose_name='début')),
                ('fin', models.DateField(blank=True, null=True, verbose_name='fin')),
                ('circonstance', models.CharField(blank=True, max_length=100, verbose_name='circonstance')),
                ('auteurs', models.ManyToManyField(blank=True, related_name='dossiers', to='libretto.Individu', verbose_name='auteurs')),
                ('categorie', models.ForeignKey(blank=True, help_text='Attention, un dossier contenu dans un autre dossier ne peut être dans une catégorie.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dossiersdevenements', to='dossiers.categoriededossiers', verbose_name='catégorie')),
                ('editeurs_scientifiques', models.ManyToManyField(related_name='dossiers_d_evenements_edites', to=settings.AUTH_USER_MODEL, verbose_name='éditeurs scientifiques')),
                ('ensembles', models.ManyToManyField(blank=True, related_name='dossiers', to='libretto.Ensemble', verbose_name='ensembles')),
                ('etat', models.ForeignKey(default=libretto.models.base._get_default_etat, on_delete=django.db.models.deletion.PROTECT, to='libretto.etat', verbose_name='état')),
                ('evenements', models.ManyToManyField(blank=True, related_name='dossiers', to='libretto.Evenement', verbose_name='événements')),
                ('lieux', models.ManyToManyField(blank=True, related_name='dossiers', to='libretto.Lieu', verbose_name='lieux')),
                ('oeuvres', models.ManyToManyField(blank=True, related_name='dossiers', to='libretto.Oeuvre', verbose_name='œuvres')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='dossierdevenements', to=settings.AUTH_USER_MODEL, verbose_name='propriétaire')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='dossiers.dossierdevenements', verbose_name='parent')),
                ('sources', models.ManyToManyField(blank=True, related_name='dossiers', to='libretto.Source', verbose_name='sources')),
                ('saisons', models.ManyToManyField(blank=True, related_name='saisons', to='libretto.Saison', verbose_name='saisons')),
                ('path', tree.fields.PathField(db_index=True, order_by=['position'])),
            ],
            options={
                'ordering': ('path',),
                'verbose_name': 'dossier d’événements',
                'verbose_name_plural': 'dossiers d’événements',
                'permissions': (('can_change_status', 'Peut changer l’état'),),
            },
        ),
        tree.operations.CreateTreeTrigger(
            model_lookup='dossierdevenements',
        ),
        tree.operations.RebuildPaths(
            model_lookup='dossierdevenements',
        ),
        migrations.RenameField(
            model_name='dossierdevenements',
            old_name='auteurs',
            new_name='individus',
        ),
        migrations.AlterField(
            model_name='dossierdevenements',
            name='individus',
            field=models.ManyToManyField(blank=True, related_name='dossiers', to='libretto.Individu', verbose_name='individus'),
        ),
        tree.operations.DeleteTreeTrigger(
            model_lookup='dossierdevenements',
        ),
        migrations.RemoveField(
            model_name='dossierdevenements',
            name='path',
        ),
        migrations.AddField(
            model_name='dossierdevenements',
            name='path',
            field=tree.fields.PathField(db_index=True, order_by=['position']),
        ),
        tree.operations.CreateTreeTrigger(
            model_lookup='dossierdevenements',
        ),
        tree.operations.RebuildPaths(
            model_lookup='dossierdevenements',
        ),
        migrations.AlterModelOptions(
            name='dossierdevenements',
            options={'ordering': ['path'], 'permissions': (('can_change_status', 'Peut changer l’état'),), 'verbose_name': 'dossier d’événements', 'verbose_name_plural': 'dossiers d’événements'},
        ),
        migrations.AlterField(
            model_name='categoriededossiers',
            name='nom',
            field=models.CharField(max_length=75, verbose_name='nom'),
        ),
        migrations.AlterField(
            model_name='categoriededossiers',
            name='position',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='position'),
        ),
        migrations.AddIndex(
            model_name='dossierdevenements',
            index=models.Index(django.db.models.expressions.RawSQL('path[:array_length(path, 1) - 1]', ()), name='dossiers_path_parent_index'),
        ),
        migrations.AddIndex(
            model_name='dossierdevenements',
            index=models.Index(django.db.models.expressions.F('path__level'), name='dossiers_path_level_index'),
        ),
        migrations.AddIndex(
            model_name='dossierdevenements',
            index=models.Index(django.db.models.expressions.F('path__0_1'), name='dossiers_path_slice_1_index'),
        ),
        migrations.AddIndex(
            model_name='dossierdevenements',
            index=models.Index(django.db.models.expressions.F('path__0_2'), name='dossiers_path_slice_2_index'),
        ),
        migrations.AddIndex(
            model_name='dossierdevenements',
            index=models.Index(django.db.models.expressions.F('path__0_3'), name='dossiers_path_slice_3_index'),
        ),
        migrations.AddIndex(
            model_name='dossierdevenements',
            index=models.Index(django.db.models.expressions.F('path__0_4'), name='dossiers_path_slice_4_index'),
        ),
        migrations.AddIndex(
            model_name='dossierdevenements',
            index=models.Index(django.db.models.expressions.F('path__0_5'), name='dossiers_path_slice_5_index'),
        ),
        migrations.AddField(
            model_name='categoriededossiers',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='dossierdevenements',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, editable=False, null=True),
        ),
        migrations.AddIndex(
            model_name='categoriededossiers',
            index=django.contrib.postgres.indexes.GinIndex(django.db.models.expressions.F('search_vector'), name='categoriededossiers_search'),
        ),
        migrations.AddIndex(
            model_name='dossierdevenements',
            index=django.contrib.postgres.indexes.GinIndex(django.db.models.expressions.F('search_vector'), name='dossierdevenements_search'),
        ),
        migrations.RemoveIndex(
            model_name='categoriededossiers',
            name='categoriededossiers_search',
        ),
        migrations.RemoveIndex(
            model_name='dossierdevenements',
            name='dossierdevenements_search',
        ),
        migrations.AddField(
            model_name='categoriededossiers',
            name='autocomplete_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='dossierdevenements',
            name='autocomplete_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, editable=False, null=True),
        ),
        migrations.AddIndex(
            model_name='categoriededossiers',
            index=django.contrib.postgres.indexes.GinIndex(django.db.models.expressions.F('search_vector'), name='categoriedossiers_search'),
        ),
        migrations.AddIndex(
            model_name='categoriededossiers',
            index=django.contrib.postgres.indexes.GinIndex(django.db.models.expressions.F('autocomplete_vector'), name='categoriedossiers_autocomplete'),
        ),
        migrations.AddIndex(
            model_name='dossierdevenements',
            index=django.contrib.postgres.indexes.GinIndex(django.db.models.expressions.F('search_vector'), name='dossierevenements_search'),
        ),
        migrations.AddIndex(
            model_name='dossierdevenements',
            index=django.contrib.postgres.indexes.GinIndex(django.db.models.expressions.F('autocomplete_vector'), name='dossierevenements_autocomplete'),
        ),
        tree.operations.DeleteTreeTrigger(
            model_lookup='dossierdevenements',
        ),
        migrations.RenameModel(
            old_name='DossierDEvenements',
            new_name='Dossier',
        ),
        migrations.RemoveIndex(
            model_name='dossier',
            name='dossierevenements_search',
        ),
        migrations.RemoveIndex(
            model_name='dossier',
            name='dossierevenements_autocomplete',
        ),
        migrations.AlterField(
            model_name='dossier',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='dossier', to=settings.AUTH_USER_MODEL, verbose_name='propriétaire'),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='categorie',
            field=models.ForeignKey(blank=True, help_text='Attention, un dossier contenu dans un autre dossier ne peut être dans une catégorie.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dossiers', to='dossiers.categoriededossiers', verbose_name='catégorie'),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='editeurs_scientifiques',
            field=models.ManyToManyField(related_name='dossiers_edites', to=settings.AUTH_USER_MODEL, verbose_name='éditeurs scientifiques'),
        ),
        migrations.AddIndex(
            model_name='dossier',
            index=django.contrib.postgres.indexes.GinIndex(django.db.models.expressions.F('search_vector'), name='dossier_search'),
        ),
        migrations.AddIndex(
            model_name='dossier',
            index=django.contrib.postgres.indexes.GinIndex(django.db.models.expressions.F('autocomplete_vector'), name='dossier_autocomplete'),
        ),
        migrations.AlterModelOptions(
            name='dossier',
            options={'ordering': ['path'], 'permissions': (('can_change_status', 'Peut changer l’état'),), 'verbose_name': 'dossier', 'verbose_name_plural': 'dossiers'},
        ),
        tree.operations.CreateTreeTrigger(
            model_lookup='dossier',
        ),
        tree.operations.RebuildPaths(
            model_lookup='dossier',
        ),
        migrations.RenameField(
            model_name='dossier',
            old_name='circonstance',
            new_name='old_circonstance',
        ),
        migrations.RenameField(
            model_name='dossier',
            old_name='debut',
            new_name='old_debut',
        ),
        migrations.RenameField(
            model_name='dossier',
            old_name='ensembles',
            new_name='old_ensembles',
        ),
        migrations.RenameField(
            model_name='dossier',
            old_name='evenements',
            new_name='old_evenements',
        ),
        migrations.RenameField(
            model_name='dossier',
            old_name='fin',
            new_name='old_fin',
        ),
        migrations.RenameField(
            model_name='dossier',
            old_name='individus',
            new_name='old_individus',
        ),
        migrations.RenameField(
            model_name='dossier',
            old_name='lieux',
            new_name='old_lieux',
        ),
        migrations.RenameField(
            model_name='dossier',
            old_name='oeuvres',
            new_name='old_oeuvres',
        ),
        migrations.RenameField(
            model_name='dossier',
            old_name='saisons',
            new_name='old_saisons',
        ),
        migrations.RenameField(
            model_name='dossier',
            old_name='sources',
            new_name='old_sources',
        ),
        migrations.AlterField(
            model_name='dossier',
            name='old_saisons',
            field=models.ManyToManyField(blank=True, related_name='dossiers', to='libretto.Saison', verbose_name='saisons'),
        ),
        migrations.CreateModel(
            name='DossierDEvenements',
            fields=[
                ('dossier_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dossiers.dossier')),
                ('debut', models.DateField(blank=True, null=True, verbose_name='début')),
                ('fin', models.DateField(blank=True, null=True, verbose_name='fin')),
                ('circonstance', models.CharField(blank=True, max_length=100, verbose_name='circonstance')),
                ('ensembles', models.ManyToManyField(blank=True, related_name='dossiersdevenements', to='libretto.Ensemble', verbose_name='ensembles')),
                ('evenements', models.ManyToManyField(blank=True, related_name='dossiersdevenements', to='libretto.Evenement', verbose_name='événements')),
                ('individus', models.ManyToManyField(blank=True, related_name='dossiersdevenements', to='libretto.Individu', verbose_name='individus')),
                ('lieux', models.ManyToManyField(blank=True, related_name='dossiersdevenements', to='libretto.Lieu', verbose_name='lieux')),
                ('oeuvres', models.ManyToManyField(blank=True, related_name='dossiersdevenements', to='libretto.Oeuvre', verbose_name='œuvres')),
                ('saisons', models.ManyToManyField(blank=True, related_name='dossiersdevenements', to='libretto.Saison', verbose_name='saisons')),
                ('sources', models.ManyToManyField(blank=True, related_name='dossiersdevenements', to='libretto.Source', verbose_name='sources')),
            ],
            options={
                'verbose_name': 'dossier d’événements',
                'verbose_name_plural': 'dossiers d’événements',
                'abstract': False,
            },
            bases=('dossiers.dossier',),
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_circonstance',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_debut',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_ensembles',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_evenements',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_fin',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_individus',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_lieux',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_oeuvres',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_saisons',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_sources',
        ),
        migrations.CreateModel(
            name='DossierDOeuvres',
            fields=[
                ('dossier_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dossiers.dossier')),
                ('debut', models.DateField(blank=True, null=True, verbose_name='début')),
                ('fin', models.DateField(blank=True, null=True, verbose_name='fin')),
                ('ensembles', models.ManyToManyField(blank=True, related_name='dossiersdoeuvres', to='libretto.Ensemble', verbose_name='ensembles')),
                ('genres', models.ManyToManyField(blank=True, related_name='dossiersdoeuvres', to='libretto.GenreDOeuvre', verbose_name='genres d’œuvre')),
                ('individus', models.ManyToManyField(blank=True, related_name='dossiersdoeuvres', to='libretto.Individu', verbose_name='individus')),
                ('lieux', models.ManyToManyField(blank=True, related_name='dossiersdoeuvres', to='libretto.Lieu', verbose_name='lieux')),
                ('sources', models.ManyToManyField(blank=True, related_name='dossiersdoeuvres', to='libretto.Source', verbose_name='sources')),
                ('oeuvres', models.ManyToManyField(blank=True, related_name='dossiersdoeuvres', to='libretto.Oeuvre', verbose_name='œuvres')),
            ],
            options={
                'verbose_name': 'dossier d’œuvres',
                'verbose_name_plural': 'dossiers d’œuvres',
                'abstract': False,
            },
            bases=('dossiers.dossier',),
        ),
        migrations.AddField(
            model_name='dossier',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='dossiers/', verbose_name='logo'),
        ),
    ]