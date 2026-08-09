# ``Individu.professions`` gains an explicit through model, ``Occupation``, so the
# Wagtail admin can offer a searchable MultipleChooserPanel. Rather than creating a
# new table and copying every row into it, the table Django had already created
# implicitly is adopted and renamed. Two steps, in this order:
#
# 1. A SeparateDatabaseAndState that adopts the existing table: the CreateModel
#    declares the current ``db_table`` and the UNIQUE constraint already on it, hence
#    ``database_operations=[]``. Nothing is created, copied or dropped; this only
#    repoints Django's model state at the table that is already there.
# 2. An AlterModelTable with ``table=None``, i.e. "use the default name", emitting
#    ``ALTER TABLE libretto_individu_professions RENAME TO libretto_occupation``.
#    The two columns already carry Django's default names (``individu_id`` and
#    ``profession_id``), so no column rename is needed.
#
# In PostgreSQL the rename is metadata-only: no rows move, and indexes, constraints
# and the id sequence keep their old names but stay attached (Django resolves them by
# introspection, never by name).

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0065_django_tree_binary_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auteur',
            name='oeuvre',
            field=modelcluster.fields.ParentalKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='auteurs', to='libretto.oeuvre', verbose_name='œuvre'),
        ),
        migrations.AlterField(
            model_name='auteur',
            name='source',
            field=modelcluster.fields.ParentalKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='auteurs', to='libretto.source', verbose_name='source'),
        ),
        migrations.AlterField(
            model_name='elementdedistribution',
            name='element_de_programme',
            field=modelcluster.fields.ParentalKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='distribution', to='libretto.elementdeprogramme', verbose_name='élément de programme'),
        ),
        migrations.AlterField(
            model_name='elementdedistribution',
            name='evenement',
            field=modelcluster.fields.ParentalKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='distribution', to='libretto.evenement', verbose_name='événement'),
        ),
        migrations.AlterField(
            model_name='elementdeprogramme',
            name='evenement',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='programme', to='libretto.evenement', verbose_name='événement'),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='debut_date',
            field=models.DateField(db_index=True, help_text='Exemple\xa0: « 1789-7-14 » pour le 14 juillet 1789. En cas de date approximative, saisir le premier jour du mois («\xa01678-10-1\xa0» pour octobre 1678) ou de l’année («\xa01830-1-1\xa0» pour 1830).', verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='fin_date',
            field=models.DateField(blank=True, db_index=True, help_text='Exemple\xa0: « 1789-7-14 » pour le 14 juillet 1789. En cas de date approximative, saisir le premier jour du mois («\xa01678-10-1\xa0» pour octobre 1678) ou de l’année («\xa01830-1-1\xa0» pour 1830).', null=True, verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='individu',
            name='deces_date',
            field=models.DateField(blank=True, db_index=True, help_text='Exemple\xa0: « 1789-7-14 » pour le 14 juillet 1789. En cas de date approximative, saisir le premier jour du mois («\xa01678-10-1\xa0» pour octobre 1678) ou de l’année («\xa01830-1-1\xa0» pour 1830).', null=True, verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='individu',
            name='naissance_date',
            field=models.DateField(blank=True, db_index=True, help_text='Exemple\xa0: « 1789-7-14 » pour le 14 juillet 1789. En cas de date approximative, saisir le premier jour du mois («\xa01678-10-1\xa0» pour octobre 1678) ou de l’année («\xa01830-1-1\xa0» pour 1830).', null=True, verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='membre',
            name='ensemble',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='membres', to='libretto.ensemble', verbose_name='ensemble'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='creation_date',
            field=models.DateField(blank=True, db_index=True, help_text='Exemple\xa0: « 1789-7-14 » pour le 14 juillet 1789. En cas de date approximative, saisir le premier jour du mois («\xa01678-10-1\xa0» pour octobre 1678) ou de l’année («\xa01830-1-1\xa0» pour 1830).', null=True, verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='saison',
            name='debut',
            field=models.DateField(help_text='Exemple\xa0: « 1789-7-14 » pour le 14 juillet 1789.', verbose_name='début'),
        ),
        migrations.AlterField(
            model_name='saison',
            name='fin',
            field=models.DateField(help_text='Exemple\xa0: « 1789-7-14 » pour le 14 juillet 1789.', verbose_name='fin'),
        ),
        migrations.AlterField(
            model_name='source',
            name='date',
            field=models.DateField(blank=True, db_index=True, help_text='Exemple\xa0: « 1789-7-14 » pour le 14 juillet 1789. En cas de date approximative, saisir le premier jour du mois («\xa01678-10-1\xa0» pour octobre 1678) ou de l’année («\xa01830-1-1\xa0» pour 1830).', null=True, verbose_name='date'),
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Occupation',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('individu', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='occupations', to='libretto.individu', verbose_name='individu')),
                        ('profession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='occupations', to='libretto.profession', verbose_name='profession')),
                    ],
                    options={
                        'verbose_name': 'occupation',
                        'verbose_name_plural': 'occupations',
                        'ordering': ('individu', 'profession'),
                        'db_table': 'libretto_individu_professions',
                        'unique_together': {('individu', 'profession')},
                    },
                ),
                migrations.AlterField(
                    model_name='individu',
                    name='professions',
                    field=models.ManyToManyField(blank=True, related_name='individus', through='libretto.Occupation', to='libretto.profession', verbose_name='professions'),
                ),
            ],
            database_operations=[],
        ),
        migrations.AlterModelTable(name='occupation', table=None),
        migrations.AlterField(
            model_name='parentedindividus',
            name='enfant',
            field=modelcluster.fields.ParentalKey(on_delete=models.deletion.PROTECT, related_name='parentes', to='libretto.individu', verbose_name='individu enfant'),
        ),
    ]
