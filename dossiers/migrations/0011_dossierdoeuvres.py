from django.db import migrations, models
import django.db.models.deletion


def create_dossier_opera_comique(apps, schema_editor):
    Dossier = apps.get_model('dossiers', 'Dossier')
    DossierDOeuvres = apps.get_model('dossiers', 'DossierDOeuvres')
    HierarchicUser = apps.get_model('accounts', 'HierarchicUser')
    Source = apps.get_model('libretto', 'Source')
    try:
        parent = Dossier.objects.get(slug="archives-opera-comique")
        dossier = DossierDOeuvres(dossier_ptr_id=parent.pk)
        dossier.save_base(raw=True)
        owner = HierarchicUser.objects.get(last_name='Opéra Comique')
        sources = list(Source.objects.filter(owner=owner))
        dossier.sources.set(sources)
    except (DossierDOeuvres.DoesNotExist, HierarchicUser.DoesNotExist):
        raise


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0059_oeuvre_ambitus'),
        ('dossiers', '0010_remove_dossier_old_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='DossierDOeuvres',
            fields=[
                ('dossier_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dossiers.dossier')),
                ('debut', models.DateField(blank=True, null=True, verbose_name='début')),
                ('fin', models.DateField(blank=True, null=True, verbose_name='fin')),
                ('ensembles', models.ManyToManyField(blank=True, related_name='dossiersdoeuvres', to='libretto.Ensemble', verbose_name='ensembles')),
                ('genres', models.ManyToManyField(blank=True, related_name='dossiersdoeuvres', to='libretto.GenreDOeuvre', verbose_name='genres d’œuvre')),
                ('individus', models.ManyToManyField(blank=True, related_name='dossiersdoeuvres', to='libretto.Individu', verbose_name='individus')),
                ('lieux', models.ManyToManyField(blank=True, related_name='dossiersdoeuvres', to='libretto.Lieu', verbose_name='lieux')),
                ('sources', models.ManyToManyField(blank=True, related_name='dossiersdoeuvres', to='libretto.Source', verbose_name='sources')),
                ('oeuvres', models.ManyToManyField(blank=True, related_name='dossiersdoeuvres', to='libretto.Oeuvre', verbose_name='œuvres')),
            ],
            options={
                'verbose_name': 'dossier d’œuvres',
                'verbose_name_plural': 'dossiers d’œuvres',
                'abstract': False,
            },
            bases=('dossiers.dossier',),
        ),
        migrations.RunPython(create_dossier_opera_comique),
    ]
