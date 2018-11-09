from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0035_auto_20170109_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='typedensemble',
            name='nom_pluriel',
            field=models.CharField(help_text='À remplir si le pluriel n’est pas un simple ajout de « s ». Exemple : « animal » devient « animaux » et non « animals ».', blank=True, verbose_name='nom pluriel', max_length=45),
        ),
    ]
