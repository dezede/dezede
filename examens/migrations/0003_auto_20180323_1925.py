from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('examens', '0002_auto_20160210_0540'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='level',
            options={'verbose_name': 'niveau', 'verbose_name_plural': 'niveaux', 'ordering': ('number',)},
        ),
        migrations.AlterModelOptions(
            name='levelsource',
            options={'verbose_name': 'source de niveau', 'verbose_name_plural': 'sources de niveau'},
        ),
        migrations.AlterModelOptions(
            name='takenexam',
            options={'verbose_name': 'examen passé', 'verbose_name_plural': 'examens passés', 'ordering': ('user', 'session')},
        ),
        migrations.AlterModelOptions(
            name='takenlevel',
            options={'verbose_name': 'niveau passé', 'verbose_name_plural': 'niveaux passés', 'ordering': ('start',)},
        ),
        migrations.AlterField(
            model_name='level',
            name='help_message',
            field=models.TextField(verbose_name='message d’aide'),
        ),
        migrations.AlterField(
            model_name='level',
            name='number',
            field=models.PositiveSmallIntegerField(verbose_name='numéro', unique=True, default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='level',
            name='sources',
            field=models.ManyToManyField(verbose_name='sources', related_name='_level_sources_+', to='libretto.Source', through='examens.LevelSource'),
        ),
        migrations.AlterField(
            model_name='levelsource',
            name='level',
            field=models.ForeignKey(verbose_name='niveau', related_name='level_sources', to='examens.Level'),
        ),
        migrations.AlterField(
            model_name='levelsource',
            name='source',
            field=models.OneToOneField(verbose_name='source', related_name='+', to='libretto.Source'),
        ),
        migrations.AlterField(
            model_name='takenexam',
            name='session',
            field=models.OneToOneField(verbose_name='session', blank=True, null=True, editable=False, related_name='+', on_delete=django.db.models.deletion.SET_NULL, to='sessions.Session'),
        ),
        migrations.AlterField(
            model_name='takenexam',
            name='user',
            field=models.OneToOneField(verbose_name='utilisateur', blank=True, null=True, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='takenlevel',
            name='end',
            field=models.DateTimeField(verbose_name='fin', blank=True, null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='takenlevel',
            name='level',
            field=models.ForeignKey(verbose_name='niveau', editable=False, related_name='+', to='examens.Level'),
        ),
        migrations.AlterField(
            model_name='takenlevel',
            name='passed',
            field=models.BooleanField(verbose_name='passé', default=False),
        ),
        migrations.AlterField(
            model_name='takenlevel',
            name='score',
            field=models.FloatField(verbose_name='note', blank=True, null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='takenlevel',
            name='source',
            field=models.ForeignKey(verbose_name='source', editable=False, related_name='+', to='libretto.Source'),
        ),
        migrations.AlterField(
            model_name='takenlevel',
            name='start',
            field=models.DateTimeField(verbose_name='début', auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='takenlevel',
            name='taken_exam',
            field=models.ForeignKey(verbose_name='examen passé', editable=False, related_name='taken_levels', to='examens.TakenExam'),
        ),
    ]
