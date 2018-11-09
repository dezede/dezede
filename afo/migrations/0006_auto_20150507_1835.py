from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('afo', '0005_add_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='evenementafo',
            name='cycle',
            field=models.CharField(max_length=40, verbose_name='cycle', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='evenementafo',
            name='remplacants',
            field=models.PositiveIntegerField(null=True, verbose_name='nombre de musiciens rempla\xe7ants', blank=True),
            preserve_default=True,
        ),
    ]
