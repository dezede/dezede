from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0029_add_auteur_ensemble_and_constraints'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='auteur',
            options={'ordering': ('profession', 'ensemble', 'individu'), 'verbose_name': 'author', 'verbose_name_plural': 'authors'},
        ),
        migrations.AddField(
            model_name='oeuvre',
            name='creation_type',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='type de cr\xe9ation', choices=[(1, 'gen\xe8se'), (2, 'premi\xe8re mondiale'), (3, 'premi\xe8re \xe9dition')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='oeuvre',
            name='indeterminee',
            field=models.BooleanField(default=False, help_text='Cocher si l\u2019\u0153uvre n\u2019est pas identifiable, par exemple un quatuor de Haydn, sans savoir lequel.', verbose_name='ind\xe9termin\xe9e'),
            preserve_default=True,
        ),
    ]
