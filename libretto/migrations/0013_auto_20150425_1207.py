from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0012_migrate_arrangements'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='caracteristiquedoeuvre',
            name='caracteristique_ptr',
        ),
        migrations.RemoveField(
            model_name='typedecaracteristiquedoeuvre',
            name='typedecaracteristique_ptr',
        ),
        migrations.DeleteModel(
            name='TypeDeCaracteristiqueDOeuvre',
        ),
        migrations.RemoveField(
            model_name='oeuvre',
            name='caracteristiques',
        ),
        migrations.DeleteModel(
            name='CaracteristiqueDOeuvre',
        ),
    ]
