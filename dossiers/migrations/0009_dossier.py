from django.conf import settings
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.expressions
from tree.operations import DeleteTreeTrigger, CreateTreeTrigger, RebuildPaths





class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0059_oeuvre_ambitus'),
        ('dossiers', '0008_add_autocomplete_vector'),
    ]

    operations = [
        # Renames old model DossierDEvenements into Dossier
        DeleteTreeTrigger('dossierdevenements'),
        migrations.RenameModel('DossierDEvenements', 'Dossier'),
        migrations.RemoveIndex(
            model_name='dossier',
            name='dossierdevenements_search',
        ),
        migrations.AlterField(
            model_name='dossier',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='dossier', to=settings.AUTH_USER_MODEL, verbose_name='propriétaire'),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='categorie',
            field=models.ForeignKey(blank=True,
                                    help_text='Attention, un dossier contenu dans un autre dossier ne peut être dans une catégorie.',
                                    null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dossiers',
                                    to='dossiers.categoriededossiers', verbose_name='catégorie'),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='editeurs_scientifiques',
            field=models.ManyToManyField(related_name='dossiers_edites', to=settings.AUTH_USER_MODEL,
                                         verbose_name='éditeurs scientifiques'),
        ),
        migrations.AddIndex(
            model_name='dossier',
            index=django.contrib.postgres.indexes.GinIndex(django.db.models.expressions.F('search_vector'),
                                                           name='dossier_search'),
        ),
        migrations.AlterModelOptions(
            name='dossier',
            options={'ordering': ['path'], 'permissions': (('can_change_status', 'Peut changer l’état'),),
                     'verbose_name': 'dossier', 'verbose_name_plural': 'dossiers'},
        ),
        CreateTreeTrigger('dossier'),
        RebuildPaths('dossier'),
        
        # Renames Dossier attributes into old_*
        # so that selector names don’t clash with future DossierDEvenements selector names.
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
            field=models.ManyToManyField(blank=True, related_name='dossiers', to='libretto.Saison',
                                         verbose_name='saisons'),
        ),
        
        # Creates new DossierDEvenements model.
        migrations.CreateModel(
            name='DossierDEvenements',
            fields=[
                ('dossier_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='dossiers.dossier')),
                ('debut', models.DateField(blank=True, null=True, verbose_name='début')),
                ('fin', models.DateField(blank=True, null=True, verbose_name='fin')),
                ('circonstance', models.CharField(blank=True, max_length=100, verbose_name='circonstance')),
                ('ensembles',
                 models.ManyToManyField(blank=True, related_name='dossiersdevenements', to='libretto.Ensemble',
                                        verbose_name='ensembles')),
                ('evenements',
                 models.ManyToManyField(blank=True, related_name='dossiersdevenements', to='libretto.Evenement',
                                        verbose_name='événements')),
                ('individus',
                 models.ManyToManyField(blank=True, related_name='dossiersdevenements', to='libretto.Individu',
                                        verbose_name='individus')),
                ('lieux', models.ManyToManyField(blank=True, related_name='dossiersdevenements', to='libretto.Lieu',
                                                 verbose_name='lieux')),
                ('oeuvres', models.ManyToManyField(blank=True, related_name='dossiersdevenements', to='libretto.Oeuvre',
                                                   verbose_name='œuvres')),
                ('saisons', models.ManyToManyField(blank=True, related_name='dossiersdevenements', to='libretto.Saison',
                                                   verbose_name='saisons')),
                ('sources', models.ManyToManyField(blank=True, related_name='dossiersdevenements', to='libretto.Source',
                                                   verbose_name='sources')),
            ],
            options={
                'verbose_name': 'dossier d’événements',
                'verbose_name_plural': 'dossiers d’événements',
                'abstract': False,
            },
            bases=('dossiers.dossier',),
        ),
    ]
