from django.db import models, migrations


def migrate_arrangements(apps, schema_editor):
    CaracteristiqueDOeuvre = apps.get_model('libretto', 'CaracteristiqueDOeuvre')
    TypeDeCaracteristiqueDOeuvre = apps.get_model('libretto', 'TypeDeCaracteristiqueDOeuvre')

    assert not CaracteristiqueDOeuvre.objects.exclude(valeur__in=('transcription', 'orchestration')).exists()

    transcription = CaracteristiqueDOeuvre.objects.filter(valeur='transcription').first()
    if transcription is not None:
        transcription.oeuvres.update(arrangement=1)

    orchestration = CaracteristiqueDOeuvre.objects.filter(valeur='orchestration').first()
    if orchestration is not None:
        orchestration.oeuvres.update(arrangement=2)

    CaracteristiqueDOeuvre.objects.all().delete()
    TypeDeCaracteristiqueDOeuvre.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('libretto', '0011_oeuvre_arrangement'),
    ]

    operations = [
        migrations.RunPython(migrate_arrangements, lambda apps, b: None)
    ]
