from django.db import models, migrations


def migrate_types_de_parente(apps, schema_editor):
    TypeDeParenteDIndividus = apps.get_model('libretto', 'TypeDeParenteDIndividus')
    TypeDeParenteDOeuvres = apps.get_model('libretto', 'TypeDeParenteDOeuvres')
    TypeDeParenteDIndividus2 = apps.get_model('libretto', 'TypeDeParenteDIndividus2')
    TypeDeParenteDOeuvres2 = apps.get_model('libretto', 'TypeDeParenteDOeuvres2')

    bulk = []
    for type in TypeDeParenteDIndividus.objects.all():
        bulk.append(TypeDeParenteDIndividus2(
            pk=type.pk,
            nom=type.nom, nom_pluriel=type.nom_pluriel,
            nom_relatif=type.nom_relatif,
            nom_relatif_pluriel=type.nom_relatif_pluriel,
            classement=type.classement,
            owner=type.owner))
    TypeDeParenteDIndividus2.objects.bulk_create(bulk)

    bulk = []
    for type in TypeDeParenteDOeuvres.objects.all():
        bulk.append(TypeDeParenteDOeuvres2(
            pk=type.pk,
            nom=type.nom, nom_pluriel=type.nom_pluriel,
            nom_relatif=type.nom_relatif,
            nom_relatif_pluriel=type.nom_relatif_pluriel,
            classement=type.classement,
            owner=type.owner))
    TypeDeParenteDOeuvres2.objects.bulk_create(bulk)


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0016_typedeparentedindividus2_typedeparentedoeuvres2'),
    ]

    operations = [
        migrations.RunPython(migrate_types_de_parente)
    ]
