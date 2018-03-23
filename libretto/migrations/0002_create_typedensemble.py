# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libretto', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TypeDEnsemble',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(help_text='In lowercase.', max_length=30, verbose_name='name')),
                ('nom_pluriel', models.CharField(help_text='\xc0 remplir si le pluriel n\u2019est pas un simple ajout de \xab s \xbb. Exemple : \xab animal \xbb devient \xab animaux \xbb et non \xab animals \xbb.', max_length=30, verbose_name='nom pluriel', blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('owner', models.ForeignKey(related_name='typedensemble', on_delete=django.db.models.deletion.PROTECT, verbose_name='propri\xe9taire', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('parent', models.ForeignKey(related_name='enfants', verbose_name='parent', blank=True, to='libretto.TypeDEnsemble', null=True)),
            ],
            options={
                'ordering': ('nom',),
                'verbose_name': 'type d\u2019ensemble',
                'verbose_name_plural': 'types d\u2019ensemble',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ensemble',
            name='type',
            field=models.ForeignKey(related_name='ensembles', to='libretto.TypeDEnsemble', null=True),
            preserve_default=True,
        ),
    ]
