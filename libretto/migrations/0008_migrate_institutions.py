from django.db import models, migrations


def migrate_institution(apps, schema_editor):
    Institution = apps.get_model('libretto', 'Institution')
    Institution.objects.update(is_institution=True)


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0007_lieu_is_institution'),
    ]

    operations = [
        migrations.RunPython(migrate_institution)
    ]
