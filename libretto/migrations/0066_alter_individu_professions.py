from django.db import migrations, models
import modelcluster.fields


def migrate_data(apps, schema_editor):
    Individu = apps.get_model('libretto', 'Individu')
    Occupation = apps.get_model('libretto', 'Occupation')
    IndividuProfession = Individu.professions.through

    occupations = [
        Occupation(individu=obj.individu, profession=obj.profession)
        for obj in IndividuProfession.objects.all()
    ]
    Occupation.objects.bulk_create(occupations)


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0065_alter_auteur_oeuvre_alter_auteur_source_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_data),
        migrations.RemoveField(model_name='individu', name='professions'),
        migrations.AddField(
            model_name='individu',
            name='professions',
            field=models.ManyToManyField(blank=True, related_name='individus', through='libretto.Occupation', to='libretto.profession', verbose_name='professions'),
        ),
        migrations.AlterField(
            model_name='parentedindividus',
            name='parent',
            field=modelcluster.fields.ParentalKey(on_delete=models.deletion.PROTECT, related_name='enfances', to='libretto.individu', verbose_name='individu parent'),
        ),
    ]
