from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


def migrate_partie_profession_data(apps, schema_editor):
    PartieProfession = apps.get_model('libretto', 'PartieProfession')
    Partie = apps.get_model('libretto', 'Partie')
    through = Partie.professions.through
    emplois = [
        PartieProfession(profession=obj.profession, partie=obj.partie)
        for obj in through.objects.all()
    ]
    PartieProfession.objects.bulk_create(emplois)


def migrate_parentedegenredoeuvre_data(apps, schema_editor):
    ParenteDeGenresDOeuvre = apps.get_model('libretto', 'ParenteDeGenresDOeuvre')
    GenreDOeuvre = apps.get_model('libretto', 'GenreDOeuvre')
    through = GenreDOeuvre.parents.through
    parentes = [
        ParenteDeGenresDOeuvre(parent=obj.to_genredoeuvre, enfant=obj.from_genredoeuvre)
        for obj in through.objects.all()
    ]
    ParenteDeGenresDOeuvre.objects.bulk_create(parentes)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libretto', '0067_alter_parentedoeuvres_mere_dedicace'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartieProfession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s', to=settings.AUTH_USER_MODEL, verbose_name='propriétaire')),
                ('partie', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.PROTECT, related_name='partie_professions', to='libretto.partie')),
                ('profession', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='partie_professions', to='libretto.profession')),
            ],
            options={
                'verbose_name': 'profession',
                'verbose_name_plural': 'professions',
                'ordering': ('partie', 'profession'),
                'abstract': False,
            },
        ),
        migrations.RunPython(migrate_partie_profession_data, migrations.RunPython.noop),
        migrations.RemoveField(model_name='Partie', name='professions'),
        migrations.AddField(
            model_name='partie',
            name='professions',
            field=models.ManyToManyField(blank=True, related_name='parties', through='libretto.PartieProfession', to='libretto.profession', verbose_name='professions'),
        ),
        migrations.CreateModel(
            name='ParenteDeGenresDOeuvre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enfant', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.PROTECT, related_name='parentes_enfant', to='libretto.genredoeuvre')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s', to=settings.AUTH_USER_MODEL, verbose_name='propriétaire')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='parentes_parent', to='libretto.genredoeuvre')),
            ],
            options={
                'verbose_name': 'parenté de genres d’œuvre',
                'verbose_name_plural': 'parentés de genres d’œuvre',
                'ordering': ('parent', 'enfant'),
                'abstract': False,
            },
        ),
        migrations.RunPython(migrate_parentedegenredoeuvre_data, migrations.RunPython.noop),
        migrations.RemoveField(model_name='GenreDOeuvre', name='parents'),
        migrations.AddField(
            model_name='genredoeuvre',
            name='parents',
            field=models.ManyToManyField(blank=True, related_name='enfants', through='libretto.ParenteDeGenresDOeuvre', to='libretto.genredoeuvre', verbose_name='parents'),
        ),
    ]
