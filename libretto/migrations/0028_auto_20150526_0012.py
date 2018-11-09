from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0027_auto_20150519_0413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elementdeprogramme',
            name='caracteristiques',
            field=models.ManyToManyField(related_name='elements_de_programme', verbose_name='caract\xe9ristiques', to='libretto.CaracteristiqueDeProgramme', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evenement',
            name='caracteristiques',
            field=models.ManyToManyField(related_name='evenements', verbose_name='caract\xe9ristiques', to='libretto.CaracteristiqueDeProgramme', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fichier',
            name='type',
            field=models.PositiveSmallIntegerField(blank=True, null=True, db_index=True, choices=[(0, 'autre'), (1, 'image'), (2, 'audio'), (3, 'vid\xe9o')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='genredoeuvre',
            name='parents',
            field=models.ManyToManyField(related_name='enfants', to='libretto.GenreDOeuvre', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='individu',
            name='professions',
            field=models.ManyToManyField(related_name='individus', verbose_name='occupations', to='libretto.Profession', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='filles',
            field=models.ManyToManyField(related_name='meres', through='libretto.ParenteDOeuvres', to='libretto.Oeuvre', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='partie',
            name='professions',
            field=models.ManyToManyField(help_text='La ou les profession(s) capable(s) de jouer ce r\xf4le ou cet instrument.', related_name='parties', verbose_name='occupations', to='libretto.Profession', blank=True),
            preserve_default=True,
        ),
    ]
