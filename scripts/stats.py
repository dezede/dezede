# coding: utf-8

from __future__ import unicode_literals, division
import datetime
import io
import time
from django.db import connection
from django.db.models import Count
from reversion.models import Revision
from accounts.templatetags.accounts_extra import log_ratio, hsv_to_hex
from libretto.models.common import OrderedDefaultDict


def run():
    print('Lancement')
    debut = time.time()

    rect_size = 20  # pixels
    date_format = '%d/%m/%Y'

    headers = 'user__first_name', 'user__last_name', 'n_revisions', 'week'
    data = Revision.objects.extra({
        'week': connection.ops.date_trunc_sql('week', 'date_created')}) \
        .values('week').annotate(n_revisions=Count('pk')).values_list(*headers).order_by('user', 'week')

    print('la requete a pris %s secondes' % (time.time() - debut))

    grouped_data = OrderedDefaultDict()
    for d in data:
        if not d[0]:
            continue
        grouped_data[' '.join(d[:2])].append(d[2:])
    data = grouped_data

    step = datetime.timedelta(weeks=1)

    with io.open('stats.html', 'w') as f:
        f.write("""
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="http://netdna.bootstrapcdn.com/twitter-bootstrap/2.3.2/css/bootstrap-combined.no-icons.min.css" rel="stylesheet">
    <style>td:first-child {text-align: right;} svg {border: 1px solid #EEE;}</style>
  </head>
  <body>
    <table>""")
        f.write('<tr>')
        f.write('<th>Utilisateur</th>')
        f.write('<th>Répartition de l’activité</th></tr>')
        maxi = max(n for v in data.values() for n, date in v)
        start = min(date for v in data.values() for n, date in v)
        end = max(date for v in data.values() for n, date in v)

        for k, v in data.items():
            f.write('<tr>')
            f.write('<td>%s</td>' % k)

            start -= datetime.timedelta(days=start.weekday())
            svg_width = rect_size * (end - start).total_seconds() / step.total_seconds()

            f.write('<td><svg width="%s" height="%s">' % (svg_width, rect_size))
            for count, date in sorted(v, key=lambda l: l[1]):
                f.write('<rect width="%s" height="%s" x="%s" style="fill: %s;" title="%s au %s : %s révisions" />' % (
                        rect_size,
                        rect_size,
                        rect_size * (date - start).total_seconds() / step.total_seconds(),
                        hsv_to_hex(0, log_ratio(count, maxi), 1),
                        date.strftime(date_format),
                        (date + step).strftime(date_format),
                        count))
            f.write('</td></svg>')
            f.write('</tr>')
        f.write("""
    </table>
    <script src="http://code.jquery.com/jquery.js"></script>
    <script src="http://netdna.bootstrapcdn.com/twitter-bootstrap/2.3.2/js/bootstrap.min.js"></script>
    <script>
      $('*[title]').tooltip({container: 'body'});
    </script>
  </body>
</html>""")

    print(time.time() - debut)
