from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libretto', '0017_migrate_types_de_parente'),
    ]

    operations = [

        migrations.AlterUniqueTogether(
            name='typedeparente',
            unique_together=None),
        migrations.RemoveField(
            model_name='typedeparente',
            name='owner'),
        migrations.RemoveField(
            model_name='typedeparente',
            name='polymorphic_ctype'),
        migrations.RemoveField(
            model_name='typedeparentedindividus',
            name='typedeparente_ptr'),
        migrations.RemoveField(
            model_name='typedeparentedoeuvres',
            name='typedeparente_ptr'),
        migrations.AlterField(
            'ParenteDIndividus', 'type',
            models.ForeignKey(
                'TypeDeParenteDIndividus2', related_name='parentes',
                verbose_name='type', on_delete=models.PROTECT)),
        migrations.AlterField(
            'ParenteDOeuvres', 'type',
            models.ForeignKey(
                'TypeDeParenteDOeuvres2', related_name='parentes',
                verbose_name='type', on_delete=models.PROTECT)),
        migrations.DeleteModel(name='TypeDeParenteDIndividus'),
        migrations.DeleteModel(name='TypeDeParenteDOeuvres'),
        migrations.DeleteModel(name='TypeDeParente'),
        migrations.RenameModel(old_name='TypeDeParenteDIndividus2',
                               new_name='TypeDeParenteDIndividus'),
        migrations.RenameModel(old_name='TypeDeParenteDOeuvres2',
                               new_name='TypeDeParenteDOeuvres'),

        #
        # Actualisation automatique
        #
        migrations.AlterField(
            model_name='typedeparentedindividus',
            name='owner',
            field=models.ForeignKey(related_name='typedeparentedindividus', on_delete=django.db.models.deletion.PROTECT, verbose_name='propri\xe9taire', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='typedeparentedoeuvres',
            name='owner',
            field=models.ForeignKey(related_name='typedeparentedoeuvres', on_delete=django.db.models.deletion.PROTECT, verbose_name='propri\xe9taire', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='typedeparentedindividus',
            unique_together=set([('nom', 'nom_relatif')]),
        ),
        migrations.AlterUniqueTogether(
            name='typedeparentedoeuvres',
            unique_together=set([('nom', 'nom_relatif')]),
        ),
    ]
