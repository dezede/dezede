from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0006_auto_20150423_1841'),
    ]

    operations = [
        migrations.AddField(
            model_name='lieu',
            name='is_institution',
            field=models.BooleanField(default=False, verbose_name='institution'),
            preserve_default=True,
        ),
    ]
