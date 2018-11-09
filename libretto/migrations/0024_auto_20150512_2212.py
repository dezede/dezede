from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0023_auto_20150430_1707'),
    ]

    operations = [
        migrations.AddField(
            model_name='elementdedistribution',
            name='element_de_programme',
            field=models.ForeignKey(related_name='distribution2', verbose_name='\xe9l\xe9ment de programme', blank=True, to='libretto.ElementDeProgramme', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='elementdedistribution',
            name='evenement',
            field=models.ForeignKey(related_name='distribution', verbose_name='\xe9v\xe9nement', blank=True, to='libretto.Evenement', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pupitre',
            name='facultatif',
            field=models.BooleanField(default=False, verbose_name='ad libitum'),
            preserve_default=True,
        ),
    ]
