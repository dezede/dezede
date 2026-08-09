# ``Source.editeurs_scientifiques`` gains an explicit through model, ``SourceUser``,
# by adopting and renaming the table Django had already created implicitly:
#
#   libretto_source_editeurs_scientifiques -> libretto_sourceuser
#   hierarchicuser_id -> user_id
#
# Django names an implicit M2M's target column after the *target model*
# (HierarchicUser), not after the field, hence the column mismatch: it is declared as
# ``db_column`` at adoption time, then renamed by dropping that ``db_column``.
# Both renames are metadata-only in PostgreSQL.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libretto', '0069_caracteristiquedeprogrammeevenement_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sourceensemble',
            options={'verbose_name': 'individu', 'verbose_name_plural': 'individus'},
        ),
        migrations.AlterModelOptions(
            name='sourceevenement',
            options={'verbose_name': 'événement', 'verbose_name_plural': 'événements'},
        ),
        migrations.AlterModelOptions(
            name='sourceindividu',
            options={'verbose_name': 'individu', 'verbose_name_plural': 'individus'},
        ),
        migrations.AlterModelOptions(
            name='sourcelieu',
            options={'verbose_name': 'lieu', 'verbose_name_plural': 'lieux'},
        ),
        migrations.AlterModelOptions(
            name='sourceoeuvre',
            options={'verbose_name': 'œuvre', 'verbose_name_plural': 'œuvres'},
        ),
        migrations.AlterModelOptions(
            name='sourcepartie',
            options={'verbose_name': 'partie', 'verbose_name_plural': 'parties'},
        ),
        migrations.AlterField(
            model_name='sourceensemble',
            name='source',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='sourceensemble_set', to='libretto.source'),
        ),
        migrations.AlterField(
            model_name='sourceevenement',
            name='source',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='sourceevenement_set', to='libretto.source'),
        ),
        migrations.AlterField(
            model_name='sourceindividu',
            name='source',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='sourceindividu_set', to='libretto.source'),
        ),
        migrations.AlterField(
            model_name='sourcelieu',
            name='source',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='sourcelieu_set', to='libretto.source'),
        ),
        migrations.AlterField(
            model_name='sourceoeuvre',
            name='source',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='sourceoeuvre_set', to='libretto.source'),
        ),
        migrations.AlterField(
            model_name='sourcepartie',
            name='source',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='sourcepartie_set', to='libretto.source'),
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='SourceUser',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('source', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='sourceuser_set', to='libretto.source')),
                        ('user', models.ForeignKey(db_column='hierarchicuser_id', on_delete=django.db.models.deletion.CASCADE, related_name='sourceuser_set', to=settings.AUTH_USER_MODEL)),
                    ],
                    options={
                        'verbose_name': 'user',
                        'verbose_name_plural': 'users',
                        'ordering': ('source', 'user'),
                        'db_table': 'libretto_source_editeurs_scientifiques',
                        'unique_together': {('source', 'user')},
                    },
                ),
                migrations.AlterField(
                    model_name='source',
                    name='editeurs_scientifiques',
                    field=models.ManyToManyField(blank=True, related_name='sources_editees', through='libretto.SourceUser', to=settings.AUTH_USER_MODEL, verbose_name='éditeurs scientifiques'),
                ),
            ],
            database_operations=[],
        ),
        migrations.AlterModelTable(name='sourceuser', table=None),
        # Dropping ``db_column`` renames the column to Django's default.
        migrations.AlterField(
            model_name='sourceuser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sourceuser_set', to=settings.AUTH_USER_MODEL),
        ),
    ]
