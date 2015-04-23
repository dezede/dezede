# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import CharField

BATCH_SIZE = 100


def fill_evenementafo_fields(apps, schema_editor):
    Evenement = apps.get_model('libretto', 'Evenement')
    EvenementAFO = apps.get_model('afo', 'EvenementAFO')
    qs = Evenement.objects.exclude(
        code_programme='', exoneres=None, payantes=None, scolaires=None,
        frequentation=None, jauge=None)
    l = []
    for obj in qs:
        l.append(EvenementAFO(
            evenement=obj, code_programme=obj.code_programme,
            exonerees=obj.exoneres, payantes=obj.payantes,
            scolaires=obj.scolaires, frequentation=obj.frequentation,
            jauge=obj.jauge))
        if len(l) == BATCH_SIZE:
            EvenementAFO.objects.bulk_create(l)
            l = []
        EvenementAFO.objects.bulk_create(l)


def delete_evenementafo(apps, schema_editor):
    apps.get_model('afo', 'EvenementAFO').objects.all().delete()


def fill_lieuafo_fields(apps, schema_editor):
    Lieu = apps.get_model('libretto', 'Lieu')
    LieuAFO = apps.get_model('afo', 'LieuAFO')
    qs = Lieu.objects.exclude(type_de_scene='', code_postal='')
    l = []
    for obj in qs:
        l.append(LieuAFO(lieu=obj, type_de_scene=obj.type_de_scene,
                         code_postal=obj.code_postal))
        if len(l) == BATCH_SIZE:
            LieuAFO.objects.bulk_create(l)
            l = []
    LieuAFO.objects.bulk_create(l)


def delete_lieuafo(apps, schema_editor):
    apps.get_model('afo', 'LieuAFO').objects.all().delete()


class Migration(migrations.Migration):

    run_before = [
        ('libretto', '0005_auto_20150423_0910')
    ]

    dependencies = [
        ('afo', '0001_initial'),
        ('libretto', '0004_auto_20150422_1719'),
    ]

    operations = [
        migrations.RunPython(fill_evenementafo_fields, delete_evenementafo),
        migrations.RunPython(fill_lieuafo_fields, delete_lieuafo),
    ]
