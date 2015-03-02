# coding: utf-8

from __future__ import unicode_literals
from datetime import datetime
from django_rq import job
from common.utils import send_pdf, send_export
from libretto.export import EvenementExporter
from libretto.models import Evenement


@job
def events_to_pdf(pk_list, user_pk, site_pk, language_code):
    evenements = Evenement.objects.filter(pk__in=pk_list)
    context = {'evenements': evenements.prefetch_all}
    template_name = 'libretto/evenement_list.tex'
    n = len(pk_list)
    subject = 'de %s événements' % n
    filename = '%s-evenements_%s' % (n, datetime.today().date().isoformat())
    send_pdf(context, template_name, subject, filename, user_pk, site_pk,
             language_code)


def export_events(extension):
    @job
    def inner(pk_list, user_pk, site_pk, language_code):
        exporter = EvenementExporter(Evenement.objects.filter(pk__in=pk_list))
        n = len(pk_list)
        subject = 'de %s événements' % n
        filename = '%s-evenements_%s' % (n, datetime.today().date().isoformat())
        send_export(exporter, extension, subject, filename, user_pk,
                    language_code)
    return inner

events_to_csv = export_events('csv')
events_to_xlsx = export_events('xlsx')
events_to_json = export_events('json')
