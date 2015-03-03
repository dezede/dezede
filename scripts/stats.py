# coding: utf-8

from __future__ import unicode_literals, division
import datetime
import io
import os
import time
from django.db import connection
from django.db.models import Count
from django.template import Context
from django.template.base import Template
from django.utils.safestring import mark_safe
from reversion.models import Revision
from accounts.templatetags.accounts_extra import log_ratio, hsv_to_hex
from libretto.models.base import OrderedDefaultDict


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
    end += datetime.timedelta(days=6-end.weekday())
    svg_width = rect_size * (end - start).total_seconds() / step.total_seconds()

    with io.open('stats.html', 'w') as f:
        html_table = """<tr>
                          <th>Utilisateur</th>
                          <th>Répartition de l’activité</th>
                        </tr>"""

        for user_name, periods in data.items():
            html_table += """
                <tr>
                  <td>%s</td>
                  <td><svg width="%s" height="%s">""" % (user_name,
                                                         svg_width, rect_size)
            for count, date in periods:
                html_table += """
                    <rect width="%s" height="%s" x="%s" style="fill: %s;"
                          title="%s au %s : %s révisions" />""" % (
                    rect_size, rect_size,
                    rect_size * (date - start).total_seconds() / step_seconds,
                    hsv_to_hex(0, log_ratio(count, maxi), 1),
                    date.strftime(date_format),
                    (date + step).strftime(date_format),
                    count)
            html_table += '</td></svg>'
            html_table += '</tr>'
        current_path = os.path.abspath(os.path.dirname(__file__))
        t = Template(open(
            os.path.join(current_path, 'templates/stats.html')).read())
        out = t.render(Context({'table': mark_safe(html_table)}))
        f.write(out)

    print(time.time() - script_start)
