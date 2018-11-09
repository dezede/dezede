from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0036_auto_20170206_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='profession',
            name='nom_feminin_pluriel',
            field=models.CharField(help_text='À remplir si le pluriel n’est pas un simple ajout de « s ». Exemple : « animal » devient « animaux » et non « animals ».', max_length=250, blank=True, verbose_name='nom (au féminin pluriel)'),
        ),
    ]
