from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


def migrate_cdp_edp(apps, schema_editor):
    CaracteristiqueDeProgrammeElementDeProgramme = apps.get_model(
        'libretto', 'CaracteristiqueDeProgrammeElementDeProgramme',
    )
    ElementDeProgramme = apps.get_model('libretto', 'ElementDeProgramme')
    through = ElementDeProgramme.caracteristiques.through
    cdp_edp = [
        CaracteristiqueDeProgrammeElementDeProgramme(
            caracteristique=obj.caracteristiquedeprogramme,
            element=obj.elementdeprogramme,
        )
        for obj in through.objects.all()
    ]
    CaracteristiqueDeProgrammeElementDeProgramme.objects.bulk_create(cdp_edp)


def migrate_evenements_edp(apps, schema_editor):
    CaracteristiqueDeProgrammeEvenement = apps.get_model(
        'libretto', 'CaracteristiqueDeProgrammeEvenement',
    )
    Evenement = apps.get_model('libretto', 'Evenement')
    through = Evenement.caracteristiques.through
    cdp_evenement = [
        CaracteristiqueDeProgrammeEvenement(
            caracteristique=obj.caracteristiquedeprogramme,
            evenement=obj.evenement,
        )
        for obj in through.objects.all()
    ]
    CaracteristiqueDeProgrammeEvenement.objects.bulk_create(cdp_evenement)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libretto', '0068_partieprofession_parentedegenredoeuvre'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaracteristiqueDeProgrammeEvenement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caracteristique', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='caracteristiquedeprogramme_evenements', to='libretto.caracteristiquedeprogramme')),
                ('evenement', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.PROTECT, related_name='caracteristiquedeprogramme_evenements', to='libretto.evenement')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s', to=settings.AUTH_USER_MODEL, verbose_name='propriétaire')),
            ],
            options={
                'verbose_name': 'caractéristique de programme',
                'verbose_name_plural': 'caractéristiques de programme',
                'ordering': ('evenement', 'caracteristique'),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CaracteristiqueDeProgrammeElementDeProgramme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caracteristique', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='caracteristiquedeprogramme_elementdeprogrammes', to='libretto.caracteristiquedeprogramme')),
                ('element', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.PROTECT, related_name='caracteristiquedeprogramme_elementdeprogrammes', to='libretto.elementdeprogramme')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s', to=settings.AUTH_USER_MODEL, verbose_name='propriétaire')),
            ],
            options={
                'verbose_name': 'caractéristique de programme',
                'verbose_name_plural': 'caractéristiques de programme',
                'ordering': ('element', 'caracteristique'),
                'abstract': False,
            },
        ),
        migrations.RunPython(migrate_evenements_edp, migrations.RunPython.noop),
        migrations.RunPython(migrate_cdp_edp, migrations.RunPython.noop),
        migrations.RemoveField(model_name='ElementDeProgramme', name='caracteristiques'),
        migrations.RemoveField(model_name='Evenement', name='caracteristiques'),
        migrations.AddField(
            model_name='elementdeprogramme',
            name='caracteristiques',
            field=models.ManyToManyField(blank=True, related_name='elements_de_programme', through='libretto.CaracteristiqueDeProgrammeElementDeProgramme', to='libretto.caracteristiquedeprogramme', verbose_name='caractéristiques'),
        ),
        migrations.AddField(
            model_name='evenement',
            name='caracteristiques',
            field=models.ManyToManyField(blank=True, related_name='evenements', through='libretto.CaracteristiqueDeProgrammeEvenement', to='libretto.caracteristiquedeprogramme', verbose_name='caractéristiques'),
        ),
    ]
