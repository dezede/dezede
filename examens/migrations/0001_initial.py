# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0032_auto_20160210_0508'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('number', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='number', default=1, unique=True)),
                ('help_message', models.TextField(verbose_name='help message')),
            ],
            options={
                'verbose_name_plural': 'levels',
                'verbose_name': 'level',
            },
        ),
        migrations.CreateModel(
            name='LevelSource',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('level', models.ForeignKey(related_name='level_sources', to='examens.Level', verbose_name='level')),
                ('source', models.OneToOneField(to='libretto.Source', verbose_name='source')),
            ],
            options={
                'verbose_name_plural': 'sources of level',
                'verbose_name': 'source of level',
            },
        ),
        migrations.CreateModel(
            name='TakenExam',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('session', models.OneToOneField(null=True, to='sessions.Session', blank=True, on_delete=django.db.models.deletion.SET_NULL, verbose_name='session')),
                ('user', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL, blank=True, verbose_name='user')),
            ],
            options={
                'verbose_name_plural': 'taken exams',
                'verbose_name': 'taken exam',
            },
        ),
        migrations.CreateModel(
            name='TakenLevel',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('transcription', models.TextField(verbose_name='transcription')),
                ('score', models.FloatField(blank=True, editable=False, verbose_name='score', null=True)),
                ('passed', models.BooleanField(verbose_name='passed', default=False)),
                ('start', models.DateTimeField(verbose_name='start', auto_now_add=True)),
                ('end', models.DateTimeField(blank=True, editable=False, verbose_name='end', null=True)),
                ('level', models.ForeignKey(to='examens.Level', editable=False, verbose_name='level')),
                ('source', models.ForeignKey(to='libretto.Source', editable=False, verbose_name='source')),
                ('taken_exam', models.ForeignKey(related_name='taken_levels', to='examens.TakenExam', editable=False, verbose_name='taken exam')),
            ],
            options={
                'verbose_name_plural': 'taken levels',
                'verbose_name': 'taken level',
            },
        ),
        migrations.AddField(
            model_name='level',
            name='sources',
            field=models.ManyToManyField(through='examens.LevelSource', verbose_name='sources', to='libretto.Source'),
        ),
    ]
