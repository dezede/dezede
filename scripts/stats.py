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
    print('Starting…')
    script_start = time.time()

    rect_size = 20  # pixels
    date_format = '%d/%m/%Y'

    headers = 'user__first_name', 'user__last_name', 'n_revisions', 'week'
    data = Revision.objects.extra({
        'week': connection.ops.date_trunc_sql('week', 'date_created')}) \
        .values('week').annotate(n_revisions=Count('pk')) \
        .values_list(*headers).order_by('user', 'week')

    data = list(data)

    print('The SQL request took %s seconds' % (time.time() - script_start))

    grouped_data = OrderedDefaultDict()
    for d in data:
        if not d[0]:
            continue
        grouped_data[' '.join(d[:2])].append(d[2:])
    data = grouped_data

    step = datetime.timedelta(weeks=1)
    step_seconds = step.total_seconds()

    maxi = max(n for v in data.values() for n, date in v)
    start = min(date for v in data.values() for n, date in v)
    start -= datetime.timedelta(days=start.weekday())
    end = max(date for v in data.values() for n, date in v)
    svg_width = rect_size * (end - start).total_seconds() / step.total_seconds()

    with io.open('stats.html', 'w') as f:
        out = """
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="http://netdna.bootstrapcdn.com/twitter-bootstrap/2.3.2/css/bootstrap-combined.no-icons.min.css" rel="stylesheet">
    <style>td:first-child {text-align: right;} svg {border: 1px solid #EEE;}</style>
  </head>
  <body>
    <table>"""
        out += '<tr>'
        out += '<th>Utilisateur</th>'
        out += '<th>Répartition de l’activité</th></tr>'

        for k, v in data.items():
            out += '<tr>'
            out += '<td>%s</td>' % k

            out += '<td><svg width="%s" height="%s">' % (svg_width, rect_size)
            for count, date in sorted(v, key=lambda l: l[1]):
                out += '<rect width="%s" height="%s" x="%s" style="fill: %s;" title="%s au %s : %s révisions" />' % (
                    rect_size,
                    rect_size,
                    rect_size * (date - start).total_seconds() / step_seconds,
                    hsv_to_hex(0, log_ratio(count, maxi), 1),
                    date.strftime(date_format),
                    (date + step).strftime(date_format),
                    count)
            out += '</td></svg>'
            out += '</tr>'
        out += """
    </table>
    <script src="http://code.jquery.com/jquery.js"></script>
    <script src="http://netdna.bootstrapcdn.com/twitter-bootstrap/2.3.2/js/bootstrap.min.js"></script>
    <script>
      $('*[title]').tooltip({container: 'body'});
    </script>
  </body>
</html>"""
        f.write(out)

    print(time.time() - script_start)
