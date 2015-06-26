# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0028_auto_20150526_0012'),
    ]

    operations = [
        migrations.AddField(
            model_name='auteur',
            name='ensemble',
            field=models.ForeignKey(related_name='auteurs', on_delete=django.db.models.deletion.PROTECT, verbose_name='ensemble', blank=True, to='libretto.Ensemble', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='auteur',
            name='individu',
            field=models.ForeignKey(related_name='auteurs', on_delete=django.db.models.deletion.PROTECT, verbose_name='individu', blank=True, to='libretto.Individu', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='ict',
            field=models.CharField(help_text='Indice de Catalogue Th\xe9matique. Exemple\xa0: \xab\xa0RV\xa042\xa0\xbb, \xab\xa0K.\xa0299d\xa0\xbb ou encore \xab\xa0Hob.\xa0XVI:24\xa0\xbb.', max_length=25, verbose_name='ICT', db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.RunSQL("""
            ALTER TABLE libretto_elementdedistribution
            ADD CONSTRAINT evenement_xor_elementdeprogramme
            CHECK (evenement_id IS NOT NULL <> element_de_programme_id IS NOT NULL);

            ALTER TABLE libretto_elementdedistribution
            ADD CONSTRAINT not_partie_and_profession
            CHECK (NOT (partie_id IS NOT NULL AND profession_id IS NOT NULL));

            ALTER TABLE libretto_auteur
            ADD CONSTRAINT oeuvre_xor_source
            CHECK (oeuvre_id IS NOT NULL <> source_id IS NOT NULL);

            ALTER TABLE libretto_auteur
            ADD CONSTRAINT individu_xor_ensemble
            CHECK (individu_id IS NOT NULL <> ensemble_id IS NOT NULL);
        """, """
            ALTER TABLE libretto_elementdedistribution
            DROP CONSTRAINT evenement_xor_elementdeprogramme;

            ALTER TABLE libretto_elementdedistribution
            DROP CONSTRAINT not_partie_and_profession;

            ALTER TABLE libretto_auteur
            DROP CONSTRAINT oeuvre_xor_source;

            ALTER TABLE libretto_auteur
            DROP CONSTRAINT individu_xor_ensemble;
        """),
    ]
