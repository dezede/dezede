from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0026_auto_20150512_2355'),
    ]

    operations = [
        migrations.RunSQL('UPDATE libretto_pupitre SET soliste = TRUE WHERE soliste IS NULL;'),
        migrations.AlterField(
            model_name='pupitre',
            name='soliste',
            field=models.BooleanField(default=False, db_index=True, verbose_name='soliste'),
            preserve_default=True,
        ),
    ]
