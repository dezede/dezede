from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0008_migrate_institutions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='institution',
            name='lieu_ptr',
        ),
        migrations.DeleteModel(
            name='Institution',
        ),
        migrations.RemoveField(
            model_name='lieudivers',
            name='lieu_ptr',
        ),
        migrations.DeleteModel(
            name='LieuDivers',
        ),
        migrations.RemoveField(
            model_name='lieu',
            name='polymorphic_ctype',
        ),
    ]
