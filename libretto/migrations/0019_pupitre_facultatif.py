from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0018_move_types_de_parente'),
    ]

    operations = [
        migrations.AddField(
            model_name='pupitre',
            name='facultatif',
            field=models.BooleanField(default=False, verbose_name='facultatif'),
            preserve_default=True,
        ),
    ]
