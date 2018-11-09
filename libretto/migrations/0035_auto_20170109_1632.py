from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0034_auto_20160704_1122'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ensemble',
            options={'ordering': ('nom',), 'verbose_name_plural': 'ensembles', 'verbose_name': 'ensemble'},
        ),
        migrations.AlterField(
            model_name='typedensemble',
            name='nom',
            field=models.CharField(help_text='En minuscules.', max_length=40, verbose_name='nom'),
        ),
    ]
