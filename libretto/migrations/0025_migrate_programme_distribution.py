# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from tqdm import tqdm


def migrate_programme_distribution(apps, schema_editor):
    ElementDeProgramme = apps.get_model('libretto.ElementDeProgramme')
    ElementDeDistribution = apps.get_model('libretto.ElementDeDistribution')

    # Retire les éléments de distribution inutilisés
    ElementDeDistribution.objects.filter(
        evenement__isnull=True, elements_de_programme__isnull=True).delete()

    programmes_distribution = ElementDeProgramme.objects.filter(
        distribution__isnull=False)
    if not programmes_distribution.exists():
        return

    random_programme = programmes_distribution.order_by('?')[0]
    random_distribution = tuple(
        random_programme.distribution.values_list('pk', flat=True))

    for eld in tqdm(ElementDeDistribution.objects.filter(
            elements_de_programme__isnull=False)):
        eld_id = eld.id
        programme = list(eld.elements_de_programme.all())
        if eld.evenement_id is not None:
            eld.evenement = None
            eld.pk = None
        for elp in programme:
            eld.element_de_programme = elp
            eld.save()
            eld.pk = eld_id
            elp.distribution.remove(eld)
            eld.pk = None
        eld.pk = eld_id
        # On doit appeler .all() deux fois pour éviter que Django
        # utilise son cache pour récupérer le compte…
        assert eld.elements_de_programme.all().all().count() == 0

    assert not programmes_distribution.all().exists()

    assert not ElementDeDistribution.objects.filter(
        evenement__isnull=True, element_de_programme__isnull=True).exists()
    assert not ElementDeDistribution.objects.filter(
        evenement__isnull=False, element_de_programme__isnull=False).exists()

    new_random_distribution = tuple(
        random_programme.distribution2.values_list('pk', flat=True))
    if random_distribution != new_random_distribution:
        raise ValueError('Les distributions sont différentes (avant/après): '
                         '%s\n%s' % (random_distribution,
                                     new_random_distribution))


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0024_auto_20150512_2212'),
    ]

    operations = [
        migrations.RunPython(migrate_programme_distribution)
    ]
