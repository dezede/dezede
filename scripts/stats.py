# coding: utf-8

from __future__ import unicode_literals
import datetime
from django.contrib.auth import get_user_model
from django.db.models import Count, Min, Max
from reversion.models import Revision


def run():
    User = get_user_model()
    headers = 'username', 'n_revisions', 'start'
    data = User.objects.annotate(
        n_revisions=Count('revision'),
        start=Min('revision__date_created')).order_by('start').values(
            *headers)
    headers = 'username', 'n_revisions'

    dates = Revision.objects.aggregate(start=Min('date_created'), end=Max('date_created'))
    step = datetime.timedelta(days=7)

    with open('stats.html', 'w') as f:
        f.write('<html><body><style>td { min-width: 20px; }</style><table>')
        f.write('<tr>')
        for head in headers:
            f.write('<th>%s</th>' % head)
        f.write('<th colspan="%s">repartition</th></tr>' % int(1 + (dates['end'] - dates['start']).total_seconds() / step.total_seconds()))
        for row in data:
            f.write('<tr>')
            for head in headers:
                f.write('<td>%s</td>' % row[head])
            start = dates['start']
            end = dates['end']
            user = User.objects.get(username=row['username'])
            maxi = 0
            while end > start:
                maxi = max(maxi, Revision.objects.filter(user=user, date_created__range=(start, start + step)).count())
                start += step

            start = dates['start'].date()
            end = dates['end'].date()
            maxi = float(maxi)
            while end > start:
                count = Revision.objects.filter(user=user, date_created__range=(start, start + step)).count()
                if maxi:
                    ratio = 5 * count / maxi
                else:
                    ratio = 0
                f.write('<td style="background-color: hsl(120, 100%%, %s%%);" title="%s au %s : %s revisions">&nbsp;</td>' % (100 / ratio if ratio else 100, start, start + step, count))
                start += step
            f.write('</tr>')
        f.write('</table></body></html>')
