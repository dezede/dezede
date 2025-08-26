from collections import OrderedDict

from rest_framework.reverse import reverse
from rest_framework.serializers import Field


class SpaceTimeSerializer(Field):
    def to_representation(self, obj):
        d = OrderedDict()
        for fieldname in sorted(obj.fields):
            d[fieldname] = getattr(obj, fieldname)
        lieu = d.get('lieu')
        if lieu is not None:
            d['lieu'] = reverse('lieu-detail', (lieu.pk,),
                                request=self.context.get('request'))
        return d
