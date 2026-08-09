# ``Oeuvre.dedicataires`` gains an explicit through model, ``Dedicace``. As in 0066,
# the table Django had already created implicitly is adopted and renamed instead of
# being recreated and refilled:
#
# 1. A SeparateDatabaseAndState adopting ``libretto_oeuvre_dedicataires`` — the
#    CreateModel declares that ``db_table`` and the UNIQUE constraint already on it,
#    hence ``database_operations=[]``.
# 2. An AlterModelTable with ``table=None`` renaming it to ``libretto_dedicace``.
#    Both columns already carry Django's default names (``oeuvre_id`` and
#    ``individu_id``), so no column rename is needed.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libretto', '0066_alter_individu_professions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pupitre',
            name='oeuvre',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='pupitres', to='libretto.oeuvre', verbose_name='œuvre'),
        ),
        migrations.AlterField(
            model_name='parentedoeuvres',
            name='fille',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='parentes_meres', to='libretto.oeuvre', verbose_name='œuvre fille'),
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Dedicace',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('individu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dedicaces', to='libretto.individu', verbose_name='individu')),
                        ('oeuvre', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='dedicaces', to='libretto.oeuvre', verbose_name='oeuvre')),
                    ],
                    options={
                        'ordering': ('oeuvre', 'individu'),
                        'verbose_name': 'dédicace',
                        'verbose_name_plural': 'dédicaces',
                        'db_table': 'libretto_oeuvre_dedicataires',
                        'unique_together': {('oeuvre', 'individu')},
                    },
                ),
                migrations.AlterField(
                    model_name='oeuvre',
                    name='dedicataires',
                    field=models.ManyToManyField(blank=True, help_text='N’ajouter que des autorités confirmées. Dans le cas contraire, utiliser les notes.', related_name='oeuvres_dediees', through='libretto.Dedicace', to='libretto.individu', verbose_name='dédié à'),
                ),
            ],
            database_operations=[],
        ),
        migrations.AlterModelTable(name='dedicace', table=None),
    ]
