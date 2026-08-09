# Dossier's ManyToManyFields gain explicit through models, so the Wagtail admin
# can offer searchable MultipleChooserPanels. Two steps, in this order:
#
# 1. A SeparateDatabaseAndState that adopts the tables Django had already
#    created implicitly for those M2Ms: each CreateModel below declares the
#    existing ``db_table`` and the columns already there, hence
#    ``database_operations=[]``. Nothing is created, copied or dropped; this
#    only repoints Django's model state at the existing tables.
# 2. Renames to Django's default names, so the models need no ``db_table`` and
#    no ``db_column`` at all:
#      - one AlterModelTable per model with ``table=None``, i.e. "use the
#        default name", emitting ``ALTER TABLE … RENAME TO
#        dossiers_<modelname>``;
#      - three AlterFields dropping a ``db_column``, emitting ``ALTER TABLE …
#        RENAME COLUMN``. Django names an implicit M2M's target column after
#        the *target model*, not the field, so these three differed:
#          editeurs_scientifiques  hierarchicuser_id -> user_id
#            (libretto/0070 renames the same column, for the same reason, on
#            Source.editeurs_scientifiques)
#          genres                  genredoeuvre_id   -> genre_id
#          types_de_sources        typedesource_id   -> type_de_source_id
#
#    In PostgreSQL both renames are metadata-only: no rows move, and indexes,
#    constraints and sequences keep their old names but stay attached (Django
#    resolves them by introspection, never by name).
#
# The renames break one hardcoded reference, updated in the same commit: the
# raw SQL in ``Dossier._get_evenements_queryset`` now reads
# ``FROM dossiers_dossierensemble``.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0070_alter_sourceensemble_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dossiers', '0015_remove_dossierdevenements_dossier_ptr_and_more'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='DossierUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dossier', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossieruser_set', to='dossiers.dossier')),
                ('user', models.ForeignKey(db_column='hierarchicuser_id', on_delete=django.db.models.deletion.CASCADE, related_name='dossieruser_set', to=settings.AUTH_USER_MODEL, verbose_name='éditeur scientifique')),
            ],
            options={
                'verbose_name': 'éditeur scientifique',
                'verbose_name_plural': 'éditeurs scientifiques',
                'db_table': 'dossiers_dossier_editeurs_scientifiques',
                'unique_together': {('dossier', 'user')},
            },
        ),
        migrations.CreateModel(
            name='DossierTypeDeSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dossier', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossiertypedesource_set', to='dossiers.dossier')),
                ('type_de_source', models.ForeignKey(db_column='typedesource_id', on_delete=django.db.models.deletion.CASCADE, related_name='dossiertypedesource_set', to='libretto.typedesource', verbose_name='type de source')),
            ],
            options={
                'verbose_name': 'type de source',
                'verbose_name_plural': 'types de source',
                'db_table': 'dossiers_dossier_types_de_sources',
                'unique_together': {('dossier', 'type_de_source')},
            },
        ),
        migrations.CreateModel(
            name='DossierSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dossier', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossiersource_set', to='dossiers.dossier')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossiersource_set', to='libretto.source', verbose_name='source')),
            ],
            options={
                'verbose_name': 'source',
                'verbose_name_plural': 'sources',
                'db_table': 'dossiers_dossier_sources',
                'unique_together': {('dossier', 'source')},
            },
        ),
        migrations.CreateModel(
            name='DossierSaison',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dossier', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossiersaison_set', to='dossiers.dossier')),
                ('saison', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossiersaison_set', to='libretto.saison', verbose_name='saison')),
            ],
            options={
                'verbose_name': 'saison',
                'verbose_name_plural': 'saisons',
                'db_table': 'dossiers_dossier_saisons',
                'unique_together': {('dossier', 'saison')},
            },
        ),
        migrations.CreateModel(
            name='DossierOeuvre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dossier', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossieroeuvre_set', to='dossiers.dossier')),
                ('oeuvre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossieroeuvre_set', to='libretto.oeuvre', verbose_name='œuvre')),
            ],
            options={
                'verbose_name': 'œuvre',
                'verbose_name_plural': 'œuvres',
                'db_table': 'dossiers_dossier_oeuvres',
                'unique_together': {('dossier', 'oeuvre')},
            },
        ),
        migrations.CreateModel(
            name='DossierLieu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dossier', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossierlieu_set', to='dossiers.dossier')),
                ('lieu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossierlieu_set', to='libretto.lieu', verbose_name='lieu')),
            ],
            options={
                'verbose_name': 'lieu',
                'verbose_name_plural': 'lieux',
                'db_table': 'dossiers_dossier_lieux',
                'unique_together': {('dossier', 'lieu')},
            },
        ),
        migrations.CreateModel(
            name='DossierIndividu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dossier', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossierindividu_set', to='dossiers.dossier')),
                ('individu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossierindividu_set', to='libretto.individu', verbose_name='individu')),
            ],
            options={
                'verbose_name': 'individu',
                'verbose_name_plural': 'individus',
                'db_table': 'dossiers_dossier_individus',
                'unique_together': {('dossier', 'individu')},
            },
        ),
        migrations.CreateModel(
            name='DossierGenre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dossier', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossiergenre_set', to='dossiers.dossier')),
                ('genre', models.ForeignKey(db_column='genredoeuvre_id', on_delete=django.db.models.deletion.CASCADE, related_name='dossiergenre_set', to='libretto.genredoeuvre', verbose_name='genre d’œuvre')),
            ],
            options={
                'verbose_name': 'genre d’œuvre',
                'verbose_name_plural': 'genres d’œuvre',
                'db_table': 'dossiers_dossier_genres',
                'unique_together': {('dossier', 'genre')},
            },
        ),
        migrations.CreateModel(
            name='DossierFiltreSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dossier', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossierfiltresource_set', to='dossiers.dossier')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossierfiltresource_set', to='libretto.source', verbose_name='source')),
            ],
            options={
                'verbose_name': 'source',
                'verbose_name_plural': 'sources',
                'db_table': 'dossiers_dossier_filtre_sources',
                'unique_together': {('dossier', 'source')},
            },
        ),
        migrations.CreateModel(
            name='DossierFiltreOeuvre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dossier', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossierfiltreoeuvre_set', to='dossiers.dossier')),
                ('oeuvre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossierfiltreoeuvre_set', to='libretto.oeuvre', verbose_name='œuvre')),
            ],
            options={
                'verbose_name': 'œuvre',
                'verbose_name_plural': 'œuvres',
                'db_table': 'dossiers_dossier_filtre_oeuvres',
                'unique_together': {('dossier', 'oeuvre')},
            },
        ),
        migrations.CreateModel(
            name='DossierEvenement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dossier', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossierevenement_set', to='dossiers.dossier')),
                ('evenement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossierevenement_set', to='libretto.evenement', verbose_name='événement')),
            ],
            options={
                'verbose_name': 'événement',
                'verbose_name_plural': 'événements',
                'db_table': 'dossiers_dossier_evenements',
                'unique_together': {('dossier', 'evenement')},
            },
        ),
        migrations.CreateModel(
            name='DossierEnsemble',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dossier', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossierensemble_set', to='dossiers.dossier')),
                ('ensemble', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossierensemble_set', to='libretto.ensemble', verbose_name='ensemble')),
            ],
            options={
                'verbose_name': 'ensemble',
                'verbose_name_plural': 'ensembles',
                'db_table': 'dossiers_dossier_ensembles',
                'unique_together': {('dossier', 'ensemble')},
            },
        ),
        migrations.AlterField(
            model_name='dossier',
            name='editeurs_scientifiques',
            field=models.ManyToManyField(related_name='dossiers_edites', through='dossiers.DossierUser', to=settings.AUTH_USER_MODEL, verbose_name='éditeurs scientifiques'),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='ensembles',
            field=models.ManyToManyField(blank=True, related_name='dossiers', through='dossiers.DossierEnsemble', to='libretto.ensemble', verbose_name='ensembles'),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='evenements',
            field=models.ManyToManyField(blank=True, related_name='dossiers', through='dossiers.DossierEvenement', to='libretto.evenement', verbose_name='événements'),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='filtre_oeuvres',
            field=models.ManyToManyField(blank=True, related_name='dossiers_filtre', through='dossiers.DossierFiltreOeuvre', to='libretto.oeuvre', verbose_name='œuvres'),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='filtre_sources',
            field=models.ManyToManyField(blank=True, related_name='dossiers_filtre', through='dossiers.DossierFiltreSource', to='libretto.source', verbose_name='sources'),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='genres',
            field=models.ManyToManyField(blank=True, related_name='dossiers', through='dossiers.DossierGenre', to='libretto.genredoeuvre', verbose_name='genres d’œuvre'),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='individus',
            field=models.ManyToManyField(blank=True, related_name='dossiers', through='dossiers.DossierIndividu', to='libretto.individu', verbose_name='individus'),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='lieux',
            field=models.ManyToManyField(blank=True, related_name='dossiers', through='dossiers.DossierLieu', to='libretto.lieu', verbose_name='lieux'),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='oeuvres',
            field=models.ManyToManyField(blank=True, related_name='dossiers', through='dossiers.DossierOeuvre', to='libretto.oeuvre', verbose_name='œuvres'),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='saisons',
            field=models.ManyToManyField(blank=True, related_name='dossiers', through='dossiers.DossierSaison', to='libretto.saison', verbose_name='saisons'),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='sources',
            field=models.ManyToManyField(blank=True, related_name='dossiers', through='dossiers.DossierSource', to='libretto.source', verbose_name='sources'),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='types_de_sources',
            field=models.ManyToManyField(blank=True, related_name='dossiers', through='dossiers.DossierTypeDeSource', to='libretto.typedesource', verbose_name='types de source'),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations,
            database_operations=[],
        ),
        # ``table=None`` means "back to Django's default", so each of these
        # renames ``dossiers_dossier_<m2m field>`` to ``dossiers_<modelname>``.
        *[migrations.AlterModelTable(name=name, table=None) for name in (
            'dossieruser',
            'dossierlieu',
            'dossierindividu',
            'dossierensemble',
            'dossiergenre',
            'dossiertypedesource',
            'dossiersaison',
            'dossierfiltreoeuvre',
            'dossierfiltresource',
            'dossierevenement',
            'dossieroeuvre',
            'dossiersource',
        )],
        # Dropping ``db_column`` renames the column to Django's default.
        migrations.AlterField(
            model_name='dossieruser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossieruser_set', to=settings.AUTH_USER_MODEL, verbose_name='éditeur scientifique'),
        ),
        migrations.AlterField(
            model_name='dossiergenre',
            name='genre',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossiergenre_set', to='libretto.genredoeuvre', verbose_name='genre d’œuvre'),
        ),
        migrations.AlterField(
            model_name='dossiertypedesource',
            name='type_de_source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dossiertypedesource_set', to='libretto.typedesource', verbose_name='type de source'),
        ),
    ]
