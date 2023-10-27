from django.db import migrations


def migrate_data(apps, schema_editor):
    Dossier = apps.get_model('dossiers', 'Dossier')
    DossierDEvenements = apps.get_model('dossiers', 'DossierDEvenements')

    old_fields = [
        field.name for field in Dossier._meta.fields
        if field.name.startswith('old_')
    ]
    old_m2m = [
        m2m.name for m2m in Dossier._meta.many_to_many
        if m2m.name.startswith('old_')
    ]

    for dossier in Dossier.objects.all():
        dossier_devenements = DossierDEvenements(
            dossier_ptr=dossier,
            **{
                old_field[len('old_'):]: getattr(dossier, old_field)
                for old_field in old_fields
            },
        )
        # Save the child instance without creating a new parent table row.
        dossier_devenements.save_base(raw=True)

        for old_m2m_name in old_m2m:
            old_values = list(getattr(dossier, old_m2m_name).only('pk'))
            getattr(dossier_devenements, old_m2m_name[len('old_'):]).set(old_values)


class Migration(migrations.Migration):

    dependencies = [
        ('dossiers', '0008_dossier'),
    ]

    operations = [
        # Migrate data
        migrations.RunPython(migrate_data),

        # Removes dossier old_* attributes
        migrations.RemoveField(
            model_name='dossier',
            name='old_circonstance',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_debut',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_ensembles',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_evenements',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_fin',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_individus',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_lieux',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_oeuvres',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_saisons',
        ),
        migrations.RemoveField(
            model_name='dossier',
            name='old_sources',
        ),
    ]
