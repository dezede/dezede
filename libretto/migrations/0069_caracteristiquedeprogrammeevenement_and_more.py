# The two ``caracteristiques`` M2Ms gain explicit through models, again by adopting
# and renaming the tables Django had already created implicitly:
#
#   Evenement.caracteristiques         -> CaracteristiqueDeProgrammeEvenement
#     libretto_evenement_caracteristiques -> libretto_caracteristiquedeprogrammeevenement
#     caracteristiquedeprogramme_id -> caracteristique_id
#
#   ElementDeProgramme.caracteristiques -> CaracteristiqueDeProgrammeElementDeProgramme
#     libretto_elementdeprogramme_caracteristiques
#       -> libretto_caracteristiquedeprogrammeelementdeprogramme
#     caracteristiquedeprogramme_id -> caracteristique_id
#     elementdeprogramme_id         -> element_id
#
# Django names an implicit M2M's columns after the *models* it joins, not after the
# fields of the new through model, hence the mismatches above: they are declared as
# ``db_column`` at adoption time, then renamed by dropping that ``db_column``.
# Both the table and the column renames are metadata-only in PostgreSQL.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libretto', '0068_partieprofession_parentedegenredoeuvre'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='CaracteristiqueDeProgrammeEvenement',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('caracteristique', models.ForeignKey(db_column='caracteristiquedeprogramme_id', on_delete=django.db.models.deletion.CASCADE, related_name='caracteristiquedeprogramme_evenements', to='libretto.caracteristiquedeprogramme')),
                        ('evenement', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='caracteristiquedeprogramme_evenements', to='libretto.evenement')),
                    ],
                    options={
                        'verbose_name': 'caractéristique de programme',
                        'verbose_name_plural': 'caractéristiques de programme',
                        'ordering': ('evenement', 'caracteristique'),
                        'db_table': 'libretto_evenement_caracteristiques',
                        'unique_together': {('evenement', 'caracteristique')},
                    },
                ),
                migrations.AlterField(
                    model_name='evenement',
                    name='caracteristiques',
                    field=models.ManyToManyField(blank=True, related_name='evenements', through='libretto.CaracteristiqueDeProgrammeEvenement', to='libretto.caracteristiquedeprogramme', verbose_name='caractéristiques'),
                ),
                migrations.CreateModel(
                    name='CaracteristiqueDeProgrammeElementDeProgramme',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('caracteristique', models.ForeignKey(db_column='caracteristiquedeprogramme_id', on_delete=django.db.models.deletion.CASCADE, related_name='caracteristiquedeprogrammeelementdeprogramme_set', to='libretto.caracteristiquedeprogramme')),
                        ('element', modelcluster.fields.ParentalKey(db_column='elementdeprogramme_id', on_delete=django.db.models.deletion.CASCADE, related_name='caracteristiquedeprogrammeelementdeprogramme_set', to='libretto.elementdeprogramme')),
                    ],
                    options={
                        'verbose_name': 'caractéristique de programme',
                        'verbose_name_plural': 'caractéristiques de programme',
                        'ordering': ('element', 'caracteristique'),
                        'db_table': 'libretto_elementdeprogramme_caracteristiques',
                        'unique_together': {('element', 'caracteristique')},
                    },
                ),
                migrations.AlterField(
                    model_name='elementdeprogramme',
                    name='caracteristiques',
                    field=models.ManyToManyField(blank=True, related_name='elements_de_programme', through='libretto.CaracteristiqueDeProgrammeElementDeProgramme', to='libretto.caracteristiquedeprogramme', verbose_name='caractéristiques'),
                ),
            ],
            database_operations=[],
        ),
        migrations.AlterModelTable(name='caracteristiquedeprogrammeevenement', table=None),
        migrations.AlterModelTable(name='caracteristiquedeprogrammeelementdeprogramme', table=None),
        # Dropping ``db_column`` renames the column to Django's default.
        migrations.AlterField(
            model_name='caracteristiquedeprogrammeevenement',
            name='caracteristique',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='caracteristiquedeprogramme_evenements', to='libretto.caracteristiquedeprogramme'),
        ),
        migrations.AlterField(
            model_name='caracteristiquedeprogrammeelementdeprogramme',
            name='caracteristique',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='caracteristiquedeprogrammeelementdeprogramme_set', to='libretto.caracteristiquedeprogramme'),
        ),
        migrations.AlterField(
            model_name='caracteristiquedeprogrammeelementdeprogramme',
            name='element',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='caracteristiquedeprogrammeelementdeprogramme_set', to='libretto.elementdeprogramme'),
        ),
    ]
