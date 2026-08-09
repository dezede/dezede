# Two more implicit M2Ms gain explicit through models, by adopting and renaming the
# tables Django had already created rather than recreating and refilling them:
#
#   Partie.professions   -> PartieProfession
#     libretto_partie_professions -> libretto_partieprofession
#     Columns already default (``partie_id``, ``profession_id``): nothing to rename.
#
#   GenreDOeuvre.parents -> ParenteDeGenresDOeuvre
#     libretto_genredoeuvre_parents -> libretto_parentedegenresdoeuvre
#     This one is self-referential, so Django named its columns ``from_<model>_id``
#     and ``to_<model>_id``. They are declared as ``db_column`` at adoption time and
#     then renamed by dropping that ``db_column``:
#       from_genredoeuvre_id -> enfant_id
#       to_genredoeuvre_id   -> parent_id
#     which reproduces exactly the mapping the previous data migration applied.
#
# Each conversion is a SeparateDatabaseAndState with ``database_operations=[]``
# (state only: the tables are already there) followed by the renames, all of which
# are metadata-only in PostgreSQL.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libretto', '0067_alter_parentedoeuvres_mere_dedicace'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='PartieProfession',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('partie', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='partieprofession_set', to='libretto.partie')),
                        ('profession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='partieprofession_set', to='libretto.profession')),
                    ],
                    options={
                        'verbose_name': 'profession',
                        'verbose_name_plural': 'professions',
                        'ordering': ('partie', 'profession'),
                        'db_table': 'libretto_partie_professions',
                        'unique_together': {('partie', 'profession')},
                    },
                ),
                migrations.AlterField(
                    model_name='partie',
                    name='professions',
                    field=models.ManyToManyField(blank=True, related_name='parties', through='libretto.PartieProfession', to='libretto.profession', verbose_name='professions'),
                ),
            ],
            database_operations=[],
        ),
        migrations.AlterModelTable(name='partieprofession', table=None),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='ParenteDeGenresDOeuvre',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('enfant', modelcluster.fields.ParentalKey(db_column='from_genredoeuvre_id', on_delete=django.db.models.deletion.CASCADE, related_name='parentes_enfant', to='libretto.genredoeuvre')),
                        ('parent', models.ForeignKey(db_column='to_genredoeuvre_id', on_delete=django.db.models.deletion.CASCADE, related_name='parentes_parent', to='libretto.genredoeuvre')),
                    ],
                    options={
                        'verbose_name': 'parenté de genres d’œuvre',
                        'verbose_name_plural': 'parentés de genres d’œuvre',
                        'ordering': ('parent', 'enfant'),
                        'db_table': 'libretto_genredoeuvre_parents',
                        'unique_together': {('enfant', 'parent')},
                    },
                ),
                migrations.AlterField(
                    model_name='genredoeuvre',
                    name='parents',
                    field=models.ManyToManyField(blank=True, related_name='enfants', through='libretto.ParenteDeGenresDOeuvre', to='libretto.genredoeuvre', verbose_name='parents'),
                ),
            ],
            database_operations=[],
        ),
        migrations.AlterModelTable(name='parentedegenresdoeuvre', table=None),
        # Dropping ``db_column`` renames the column to Django's default.
        migrations.AlterField(
            model_name='parentedegenresdoeuvre',
            name='enfant',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='parentes_enfant', to='libretto.genredoeuvre'),
        ),
        migrations.AlterField(
            model_name='parentedegenresdoeuvre',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parentes_parent', to='libretto.genredoeuvre'),
        ),
    ]
