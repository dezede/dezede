from django.db import models, migrations


def add_owner(apps, schema_editor):
    LieuAFO = apps.get_model('afo', 'LieuAFO')
    EvenementAFO = apps.get_model('afo', 'EvenementAFO')
    if not LieuAFO.objects.exists() and not EvenementAFO.objects.exists():
        return
    owner = apps.get_model('accounts', 'Hierarchicuser').objects.get(
        username='afo')
    LieuAFO.objects.update(owner=owner)
    EvenementAFO.objects.update(owner=owner)


def remove_owner(apps, schema_editor):
    apps.get_model('afo', 'LieuAFO').objects.update(owner=None)
    apps.get_model('afo', 'EvenementAFO').objects.update(owner=None)


class Migration(migrations.Migration):

    dependencies = [
        ('afo', '0004_auto_20150430_1721'),
    ]

    operations = [
        migrations.RunPython(add_owner, remove_owner),
    ]
