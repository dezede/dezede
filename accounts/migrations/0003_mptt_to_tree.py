from django.db import migrations, models
import tree.fields
from django.conf import settings
from tree.operations import CreateTreeTrigger, RebuildPaths


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20160226_1548'),
        ('tree', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hierarchicuser',
            name='level',
        ),
        migrations.RemoveField(
            model_name='hierarchicuser',
            name='lft',
        ),
        migrations.RemoveField(
            model_name='hierarchicuser',
            name='rght',
        ),
        migrations.RemoveField(
            model_name='hierarchicuser',
            name='tree_id',
        ),
        migrations.AddField(
            model_name='hierarchicuser',
            name='path',
            field=tree.fields.PathField(db_index=True, order_by=('last_name', 'first_name', 'username')),
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='avatar',
            field=models.ImageField(verbose_name='photographie d’identité', blank=True, null=True, upload_to='avatars/'),
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='mentor',
            field=models.ForeignKey(verbose_name='responsable scientifique', blank=True, null=True, related_name='disciples', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='willing_to_be_mentor',
            field=models.BooleanField(verbose_name='Veut être responsable scientifique', default=False),
        ),
        CreateTreeTrigger('hierarchicuser', parent_field='mentor'),
        RebuildPaths('hierarchicuser'),
    ]
