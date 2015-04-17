# coding: utf-8
from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django.db import transaction
from libretto.forms import SaisonForm
from libretto.models import Saison


SAISONS = {
    # "orchestre d'auvergne"
    245: (('2012-08-01', '2013-06-30'),),
    # 'orchestre de chambre de paris'
    202: (('2010-09-01', '2011-07-31'), ('2011-09-01', '2012-08-31'),
          ('2012-09-01', '2013-07-31')),
    # 'orchestre de chambre de toulouse'
    208: (('2010-09-01', '2011-08-31'), ('2011-09-01', '2012-08-31'),
          ('2012-09-01', '2013-08-31')),
    # "orchestre de l'opéra de rouen haute-normandie"
    207: (('2010-09-01', '2011-06-30'), ('2011-09-01', '2012-07-31'),
          ('2012-09-01', '2013-07-31')),
    # 'orchestre de paris'
    206: (('2010-09-01', '2011-07-31'), ('2011-08-01', '2012-07-31'),
          ('2012-08-01', '2013-07-31')),
    # 'orchestre de picardie'
    197: (('2010-09-01', '2011-07-31'), ('2011-09-01', '2012-07-31'),
          ('2012-09-01', '2013-07-31')),
    # 'orchestre national d’île-de-france'
    196: (('2010-09-01', '2011-08-31'), ('2011-09-01', '2012-07-31'),
          ('2013-08-01', '2013-08-31')),
    # 'orchestre national de lorraine'
    203: (('2010-08-01', '2011-06-30'), ('2011-09-01', '2012-07-31'),
          ('2012-08-01', '2013-07-31')),
    # 'orchestre national de montpellier languedoc roussillon'
    198: (('2010-09-01', '2011-07-31'), ('2011-09-01', '2012-07-31'),
          ('2012-09-01', '2013-07-31')),
    # 'orchestre national des pays de la loire'
    199: (('2010-09-01', '2011-07-31'), ('2011-08-01', '2012-06-30'),
          ('2012-09-01', '2013-07-31')),
    # 'orchestre poitou-charentes'
    200: (('2010-11-01', '2011-07-31'), ('2011-10-01', '2012-07-31'),
          ('2012-10-01', '2013-07-31')),
    # 'orchestre régional de basse-normandie'
    244: (('2010-09-01', '2011-07-31'), ('2011-09-01', '2012-07-31'),
          ('2012-08-01', '2013-07-31')),
    # 'orchestre symphonique et lyrique de nancy'
    204: (('2010-09-01', '2011-06-30'), ('2011-09-01', '2012-07-31'),
          ('2012-09-01', '2013-07-31')),
    # 'orchestre français des jeunes'
    242: (('2008-01-01', '2008-12-31'), ('2009-01-01', '2009-12-31'),
          ('2010-01-01', '2010-12-31'), ('2011-01-01', '2011-12-31'),
          ('2012-01-01', '2012-12-31')),
}


OWNERS = {203: 293, 198: 288, 197: 287, 206: 296, 207: 297, 208: 298, 202: 292,
          199: 289, 196: 286, 200: 290, 244: 291, 204: 294, 242: 318, 245: 295}


@transaction.atomic
def run():
    for pk, bounds in SAISONS.items():
        for debut, fin in bounds:
            form = SaisonForm({'debut': debut, 'fin': fin, 'ensemble': pk,
                               'owner': OWNERS[pk]})
            s = form.errors
            if s:
                raise ValidationError(s.get('__all__'))
            Saison.objects.create(**form.cleaned_data)