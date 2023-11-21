from django.db import migrations, models
import django.db.models.deletion


def copy_fk_into_m2m(apps, schema_editor):
    Oeuvre = apps.get_model('libretto', 'Oeuvre')
    for oeuvre in Oeuvre.objects.filter(dedicataire__isnull=False):
        oeuvre.dedicataires.add(oeuvre.dedicataire)
        oeuvre.dedicataire = None


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0060_oeuvre_ambitus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oeuvre',
            name='dedicataire',
            field=models.ForeignKey(blank=True,
                                    help_text='N’ajouter que des autorités confirmées. Dans le cas contraire, utiliser les notes.',
                                    null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='dedicaces_old', to='libretto.individu', verbose_name='dédié à'),
        ),
        migrations.AddField(
            model_name='oeuvre',
            name='dedicataires',
            field=models.ManyToManyField(blank=True, help_text='N’ajouter que des autorités confirmées. Dans le cas contraire, utiliser les notes.', related_name='dedicaces', to='libretto.Individu', verbose_name='dédié à'),
        ),
        migrations.RunPython(copy_fk_into_m2m),
        migrations.RemoveField(
            model_name='oeuvre',
            name='dedicataire',
        ),
    ]
