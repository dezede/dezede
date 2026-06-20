from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


def migrate_data(apps, schema_editor):
    Dedicace = apps.get_model('libretto', 'Dedicace')
    Oeuvre = apps.get_model('libretto', 'Oeuvre')
    through = Oeuvre.dedicataires.through
    dedicaces = [
        Dedicace(individu=obj.individu, oeuvre=obj.oeuvre)
        for obj in through.objects.all()
    ]
    Dedicace.objects.bulk_create(dedicaces)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libretto', '0066_alter_individu_professions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pupitre',
            name='oeuvre',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='pupitres', to='libretto.oeuvre', verbose_name='œuvre'),
        ),
        migrations.AlterField(
            model_name='parentedoeuvres',
            name='fille',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='parentes_meres', to='libretto.oeuvre', verbose_name='œuvre fille'),
        ),
        migrations.CreateModel(
            name='Dedicace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('individu', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dedicaces', to='libretto.individu', verbose_name='individu')),
                ('oeuvre', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.PROTECT, related_name='dedicaces', to='libretto.oeuvre', verbose_name='oeuvre')),
            ],
            options={
                'ordering': ('oeuvre', 'individu'),
                'verbose_name': 'dédicace',
                'verbose_name_plural': 'dédicaces',
            },
        ),
        migrations.RunPython(migrate_data, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='oeuvre',
            name='dedicataires',
        ),

        migrations.AddField(
            model_name='oeuvre',
            name='dedicataires',
            field=models.ManyToManyField(blank=True, help_text='N’ajouter que des autorités confirmées. Dans le cas contraire, utiliser les notes.', related_name='oeuvres_dediees', through='libretto.Dedicace', to='libretto.individu', verbose_name='dédié à'),
        ),
    ]
