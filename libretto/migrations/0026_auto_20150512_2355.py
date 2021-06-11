from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0025_migrate_programme_distribution'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='elementdeprogramme',
            name='distribution',
        ),
        migrations.AlterField(
            model_name='elementdedistribution',
            name='element_de_programme',
            field=models.ForeignKey(related_name='distribution', verbose_name='\xe9l\xe9ment de programme', blank=True, to='libretto.ElementDeProgramme', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
