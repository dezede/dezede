from django.db import models, migrations


def migrate_parties(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Partie = apps.get_model('libretto', 'Partie')
    Instrument = apps.get_model('libretto', 'Instrument')
    Role = apps.get_model('libretto', 'Role')

    assert not Partie.objects.exclude(type=0).exists()
    assert not Partie.objects.filter(oeuvre2__isnull=False).exists()

    Instrument.objects.update(type=1)
    Role.objects.update(type=2)
    for role in Role.objects.filter(oeuvre__isnull=False):
        role.oeuvre2 = role.oeuvre
        role.save()

    assert not Partie.objects.filter(type=0).exists()


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0021_add_partie_type_oeuvre'),
    ]

    operations = [
        migrations.RunPython(migrate_parties),
    ]
