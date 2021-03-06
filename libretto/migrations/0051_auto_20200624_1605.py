# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-06-24 14:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0050_auto_20200511_1301'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='membre',
            options={'ordering': ('classement', 'individu__nom', 'individu__prenoms'), 'verbose_name': 'membre', 'verbose_name_plural': 'membres'},
        ),
        migrations.AddField(
            model_name='partie',
            name='premier_interprete',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='parties_creees', to='libretto.Individu', verbose_name='premier interprète'),
        ),
    ]
