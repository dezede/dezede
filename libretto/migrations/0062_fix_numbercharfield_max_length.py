# Generated by Django 3.2.13 on 2023-11-14 15:53

import django.core.validators
from django.db import migrations
from tree.operations import DeleteTreeTrigger, CreateTreeTrigger, RebuildPaths

import libretto.models.base


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0061_change_dedicataire_into_dedicataires'),
    ]

    operations = [
        DeleteTreeTrigger('oeuvre'),
        migrations.AlterField(
            model_name='oeuvre',
            name='numero',
            field=libretto.models.base.NumberCharField(blank=True, db_index=True, help_text='Exemple\xa0: «\xa05\xa0» pour symphonie n°\xa05, «\xa07a\xa0» pour valse n°\xa07\u202fa, ou encore «\xa03-7\xa0» pour sonates n°\xa03 à\xa07. <strong>Ne pas confondre avec le sous-numéro d’opus.</strong>', max_length=11, validators=[django.core.validators.RegexValidator('^[\\d\\w\\-]+$', 'Vous ne pouvez saisir que des chiffres, lettres non accentuées et tiret, le tout sans espace.')], verbose_name='numéro'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='numero_extrait',
            field=libretto.models.base.NumberCharField(blank=True, db_index=True, help_text='Le numéro de l’extrait au sein de l’œuvre, par exemple «\xa03\xa0» pour le 3<sup>e</sup> mouvement d’un concerto, «\xa04\xa0» pour l’acte IV d’un opéra, ou encore «\xa012b\xa0».', max_length=11, validators=[django.core.validators.RegexValidator('^([1-9]\\d*)([^\\d\\.\\-]*)$', 'Vous devez saisir un nombre en chiffres arabes éventellement suivi de lettres.')], verbose_name='numéro d’extrait'),
        ),
        migrations.AlterField(
            model_name='source',
            name='numero',
            field=libretto.models.base.NumberCharField(blank=True, db_index=True, help_text='Sans «\xa0№\xa0». Exemple\u202f: «\xa052\xa0»', max_length=51, verbose_name='numéro'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='numero',
            field=libretto.models.base.NumberCharField(blank=True, db_index=True, help_text='Exemple\xa0: «\xa05\xa0» pour symphonie n°\xa05, «\xa07a\xa0» pour valse n°\xa07\u202fa, ou encore «\xa03-7\xa0» pour sonates n°\xa03 à\xa07. <strong>Ne pas confondre avec le sous-numéro d’opus.</strong>', max_length=10, validators=[django.core.validators.RegexValidator('^[\\d\\w\\-]+$', 'Vous ne pouvez saisir que des chiffres, lettres non accentuées et tiret, le tout sans espace.')], verbose_name='numéro'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='numero_extrait',
            field=libretto.models.base.NumberCharField(blank=True, db_index=True, help_text='Le numéro de l’extrait au sein de l’œuvre, par exemple «\xa03\xa0» pour le 3<sup>e</sup> mouvement d’un concerto, «\xa04\xa0» pour l’acte IV d’un opéra, ou encore «\xa012b\xa0».', max_length=10, validators=[django.core.validators.RegexValidator('^([1-9]\\d*)([^\\d\\.\\-]*)$', 'Vous devez saisir un nombre en chiffres arabes éventellement suivi de lettres.')], verbose_name='numéro d’extrait'),
        ),
        migrations.AlterField(
            model_name='source',
            name='numero',
            field=libretto.models.base.NumberCharField(blank=True, db_index=True, help_text='Sans «\xa0№\xa0». Exemple\u202f: «\xa052\xa0»', max_length=50, verbose_name='numéro'),
        ),
        CreateTreeTrigger('oeuvre'),
        RebuildPaths('oeuvre'),
    ]