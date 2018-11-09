from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('afo', '0003_auto_20150424_2353'),
    ]

    operations = [
        migrations.AddField(
            model_name='evenementafo',
            name='owner',
            field=models.ForeignKey(related_name='evenementafo', on_delete=django.db.models.deletion.PROTECT, verbose_name='propri\xe9taire', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lieuafo',
            name='owner',
            field=models.ForeignKey(related_name='lieuafo', on_delete=django.db.models.deletion.PROTECT, verbose_name='propri\xe9taire', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
