# Generated by Django 3.2.13 on 2023-07-18 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0056_add_search_vectors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oeuvre',
            name='sujet',
            field=models.CharField(blank=True, db_index=True, help_text='Exemple\xa0: «\xa0un thème de Beethoven\xa0» pour une variation sur un thème de Beethoven, «\xa0des motifs de &lt;em&gt;Lucia di Lammermoor&lt;/em&gt;\xa0» pour une fantaisie sur des motifs de <em>Lucia di Lammermoor</em> (&lt;em&gt; et &lt;/em&gt; sont les balises HTML pour mettre en emphase).', max_length=80, verbose_name='sujet'),
        ),
    ]
