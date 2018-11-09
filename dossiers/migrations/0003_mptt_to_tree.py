from django.db import migrations, models
import tree.fields
from tree.operations import CreateTreeTrigger, RebuildPaths


class Migration(migrations.Migration):

    dependencies = [
        ('dossiers', '0002_auto_20150527_0059'),
        ('tree', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dossierdevenements',
            options={'verbose_name': 'dossier d’événements', 'verbose_name_plural': 'dossiers d’événements', 'ordering': ('path',), 'permissions': (('can_change_status', 'Peut changer l’état'),)},
        ),
        migrations.RemoveField(
            model_name='dossierdevenements',
            name='level',
        ),
        migrations.RemoveField(
            model_name='dossierdevenements',
            name='lft',
        ),
        migrations.RemoveField(
            model_name='dossierdevenements',
            name='rght',
        ),
        migrations.RemoveField(
            model_name='dossierdevenements',
            name='tree_id',
        ),
        migrations.AddField(
            model_name='dossierdevenements',
            name='path',
            field=tree.fields.PathField(db_index=True, order_by=('position',)),
        ),
        migrations.AlterField(
            model_name='dossierdevenements',
            name='auteurs',
            field=models.ManyToManyField(verbose_name='auteurs', blank=True, related_name='dossiers', to='libretto.Individu'),
        ),
        migrations.AlterField(
            model_name='dossierdevenements',
            name='evenements',
            field=models.ManyToManyField(verbose_name='événements', blank=True, related_name='dossiers', to='libretto.Evenement'),
        ),
        migrations.AlterField(
            model_name='dossierdevenements',
            name='parent',
            field=models.ForeignKey(verbose_name='parent', blank=True, null=True, related_name='children', to='dossiers.DossierDEvenements'),
        ),
        migrations.AlterField(
            model_name='dossierdevenements',
            name='slug',
            field=models.SlugField(unique=True, help_text='Personnaliser l’affichage du titre du dossier dans l’adresse URL.'),
        ),
        CreateTreeTrigger('dossierdevenements'),
        RebuildPaths('dossierdevenements'),
    ]
