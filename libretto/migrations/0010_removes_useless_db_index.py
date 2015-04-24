# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0009_auto_20150423_2042'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pupitre',
            options={'ordering': ('-soliste', 'partie'), 'verbose_name': 'pupitre', 'verbose_name_plural': 'pupitres'},
        ),
        migrations.AlterField(
            model_name='elementdeprogramme',
            name='autre',
            field=models.CharField(max_length=500, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='engagement',
            name='individus',
            field=models.ManyToManyField(related_name='engagements', to='libretto.Individu'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evenement',
            name='circonstance',
            field=models.CharField(max_length=500, verbose_name='circonstance', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evenement',
            name='debut_date_approx',
            field=models.CharField(help_text='Ne remplir que si la date est impr\xe9cise.', max_length=60, verbose_name='date (approximative)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evenement',
            name='debut_heure_approx',
            field=models.CharField(help_text='Ne remplir que si l\u2019heure est impr\xe9cise.', max_length=30, verbose_name='heure (approximative)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evenement',
            name='debut_lieu_approx',
            field=models.CharField(help_text='Ne remplir que si le lieu (ou institution) est impr\xe9cis(e).', max_length=50, verbose_name='lieu (approximatif)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evenement',
            name='fin_date_approx',
            field=models.CharField(help_text='Ne remplir que si la date est impr\xe9cise.', max_length=60, verbose_name='date (approximative)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evenement',
            name='fin_heure_approx',
            field=models.CharField(help_text='Ne remplir que si l\u2019heure est impr\xe9cise.', max_length=30, verbose_name='heure (approximative)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evenement',
            name='fin_lieu_approx',
            field=models.CharField(help_text='Ne remplir que si le lieu (ou institution) est impr\xe9cis(e).', max_length=50, verbose_name='lieu (approximatif)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='individu',
            name='deces_date_approx',
            field=models.CharField(help_text='Ne remplir que si la date est impr\xe9cise.', max_length=60, verbose_name='date (approximative)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='individu',
            name='deces_lieu_approx',
            field=models.CharField(help_text='Ne remplir que si le lieu (ou institution) est impr\xe9cis(e).', max_length=50, verbose_name='lieu (approximatif)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='individu',
            name='naissance_date_approx',
            field=models.CharField(help_text='Ne remplir que si la date est impr\xe9cise.', max_length=60, verbose_name='date (approximative)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='individu',
            name='naissance_lieu_approx',
            field=models.CharField(help_text='Ne remplir que si le lieu (ou institution) est impr\xe9cis(e).', max_length=50, verbose_name='lieu (approximatif)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='creation_date_approx',
            field=models.CharField(help_text='Ne remplir que si la date est impr\xe9cise.', max_length=60, verbose_name='date (approximative)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='creation_heure_approx',
            field=models.CharField(help_text='Ne remplir que si l\u2019heure est impr\xe9cise.', max_length=30, verbose_name='heure (approximative)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='creation_lieu_approx',
            field=models.CharField(help_text='Ne remplir que si le lieu (ou institution) est impr\xe9cis(e).', max_length=50, verbose_name='lieu (approximatif)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='partie',
            name='professions',
            field=models.ManyToManyField(related_name='parties', to='libretto.Profession', blank=True, help_text='La ou les profession(s) capable(s) de jouer ce r\xf4le ou cet instrument.', null=True, verbose_name='occupations'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='personnel',
            name='engagements',
            field=models.ManyToManyField(related_name='personnels', to='libretto.Engagement'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pupitre',
            name='quantite_max',
            field=models.IntegerField(default=1, verbose_name='quantit\xe9 maximale'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pupitre',
            name='quantite_min',
            field=models.IntegerField(default=1, verbose_name='quantit\xe9 minimale'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='source',
            name='date_approx',
            field=models.CharField(help_text='Ne remplir que si la date est impr\xe9cise.', max_length=60, verbose_name='date (approximative)', blank=True),
            preserve_default=True,
        ),
    ]
