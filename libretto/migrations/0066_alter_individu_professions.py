from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


def migrate_data(apps, schema_editor):
    Individu = apps.get_model('libretto', 'Individu')
    Occupation = apps.get_model('libretto', 'Occupation')
    IndividuProfession = Individu.professions.through

    occupations = [
        Occupation(individu=obj.individu, profession=obj.profession)
        for obj in IndividuProfession.objects.all()
    ]
    Occupation.objects.bulk_create(occupations)


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
            },
        ),
        migrations.RunPython(migrate_data),
        migrations.RemoveField(model_name='individu', name='professions'),
        migrations.AddField(
            model_name='individu',
            name='professions',
            field=models.ManyToManyField(blank=True, related_name='individus', through='libretto.Occupation', to='libretto.profession', verbose_name='professions'),
        ),
        migrations.AlterField(
            model_name='parentedindividus',
            name='enfant',
            field=modelcluster.fields.ParentalKey(on_delete=models.deletion.PROTECT, related_name='parentes', to='libretto.individu', verbose_name='individu enfant'),
        ),
    ]
