from django.db import migrations, models
import tree.fields
from tree.operations import CreateTreeTrigger, RebuildPaths


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0037_profession_nom_feminin_pluriel'),
        ('tree', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='oeuvre',
            name='level',
        ),
        migrations.RemoveField(
            model_name='oeuvre',
            name='lft',
        ),
        migrations.RemoveField(
            model_name='oeuvre',
            name='rght',
        ),
        migrations.RemoveField(
            model_name='oeuvre',
            name='tree_id',
        ),
        migrations.AddField(
            model_name='lieu',
            name='path',
            field=tree.fields.PathField(db_index=True, order_by=('nom',)),
        ),
        migrations.AddField(
            model_name='oeuvre',
            name='path',
            field=tree.fields.PathField(db_index=True, order_by=('type_extrait', 'numero_extrait', 'titre', 'genre', 'numero', 'coupe', 'incipit', 'tempo', 'tonalite', 'sujet', 'arrangement', 'surnom', 'nom_courant', 'opus', 'ict')),
        ),
        migrations.AlterField(
            model_name='lieu',
            name='parent',
            field=models.ForeignKey(verbose_name='parent', blank=True, null=True, related_name='enfants', to='libretto.Lieu'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='extrait_de',
            field=models.ForeignKey(verbose_name='extrait de', blank=True, null=True, related_name='enfants', to='libretto.Oeuvre'),
        ),
        migrations.AlterField(
            model_name='partie',
            name='professions',
            field=models.ManyToManyField(verbose_name='professions', blank=True, related_name='parties', to='libretto.Profession'),
        ),
        migrations.AlterIndexTogether(
            name='lieu',
            index_together=set([]),
        ),
        migrations.RemoveField(
            model_name='lieu',
            name='level',
        ),
        migrations.RemoveField(
            model_name='lieu',
            name='lft',
        ),
        migrations.RemoveField(
            model_name='lieu',
            name='rght',
        ),
        migrations.RemoveField(
            model_name='lieu',
            name='tree_id',
        ),
        CreateTreeTrigger('lieu'),
        RebuildPaths('lieu'),
        CreateTreeTrigger('oeuvre', parent_field='extrait_de'),
        RebuildPaths('oeuvre'),
    ]
