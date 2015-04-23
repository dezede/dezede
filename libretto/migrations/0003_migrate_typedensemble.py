# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from libretto.api.models.utils import SetDefaultOwner


TYPES = (
    (u'ballet', '', ''),
    (u'brass band', u'brass band', ''),
    (u'chœur', '', ''),
    (u'chœur d’enfants', u'chœurs d’enfants', u'chœur'),
    (u'collectif', '', ''),
    (u'compagnie de danse', u'compagnies de danse', ''),
    (u'compagnie de théâtre', u'compagnies de théâtre', ''),
    (u'duo de percussionnistes', u'duos de percussionnistes', ''),
    (u'ensemble', '', ''),
    (u'ensemble de cuivres', u'ensembles de cuivres', ''),
    (u'ensemble de musique baroque', u'ensembles de musique baroque', ''),
    (u'ensemble vocal', u'ensembles vocaux', ''),
    (u'groupe', '', ''),
    (u'orchestre', '', ''),
    (u'pianistes', u'pianistes', ''),
    (u'quatuor à cordes', u'quatuors à cordes', '')
)


def migrate_typedensemble(apps, schema_editor):
    HierarchicUser = apps.get_model('accounts', 'HierarchicUser')
    Ensemble = apps.get_model('libretto', 'Ensemble')
    TypeDEnsemble = apps.get_model('libretto', 'TypeDEnsemble')
    CaracteristiqueDEnsemble = apps.get_model('libretto',
                                              'CaracteristiqueDEnsemble')
    TypeDeCaracteristiqueDEnsemble = apps.get_model(
        'libretto', 'TypeDeCaracteristiqueDEnsemble')

    if TypeDeCaracteristiqueDEnsemble.objects.count() == 0:
        return

    assert TypeDeCaracteristiqueDEnsemble.objects.count() == 1

    bertrand = HierarchicUser.objects.get(
        username='bertrand')
    with SetDefaultOwner(bertrand):
        d = {}
        for type_nom, type_nom_pluriel, type_parent_nom in TYPES:
            d[type_nom] = TypeDEnsemble.objects.create(
                nom=type_nom, nom_pluriel=type_nom_pluriel,
                parent=d.get(type_parent_nom, None),
                lft=0, rght=0, tree_id=0, level=0)
        for ens in Ensemble.objects.all():
            if ens.caracteristiques.exists():
                type_nom = ens.caracteristiques.get().valeur
                if type_nom not in d:
                    d[type_nom] = TypeDEnsemble.objects.create(
                        nom=type_nom, lft=0, rght=0, tree_id=0, level=0)
                ens.type = d[type_nom]
            else:
                type_nom = ''
                nom = ens.nom.lower()
                if nom.startswith(u'orchestre'):
                    type_nom = u'orchestre'
                elif u'ballet' not in nom and (
                        nom.startswith(u'choeur')
                        or nom.startswith(u'chœur')
                        or nom.startswith(u'chorale')):
                    type_nom = u'chœur'
                elif nom.startswith(u'ballet'):
                    type_nom = u'ballet'
                if not type_nom:
                    continue
                ens.type = d[type_nom]
            ens.save()
            ens.caracteristiques.clear()
    CaracteristiqueDEnsemble.objects.all().delete()
    TypeDeCaracteristiqueDEnsemble.objects.all().delete()
    assert not TypeDEnsemble.objects.filter(ensembles=None).exists()
    print(u'Pense à faire un `TypeDEnsemble.objects.rebuild()`.')


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0002_create_typedensemble'),
    ]

    operations = [
        migrations.RunPython(migrate_typedensemble)
    ]
