from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django_rq import job

from common.utils.export import send_pdf, send_export
from libretto.export import EvenementExporter
from libretto.models import Evenement


@job
def events_to_pdf(pk_list, user_pk, site_pk, language_code):
    evenements = Evenement.objects.filter(pk__in=pk_list)
    context = {'evenements': evenements.prefetch_all}
    template_name = 'libretto/evenement_list.tex'
    n = len(pk_list)
    subject = _('de %s événements') % n
    filename = '%s-evenements_%s' % (n, datetime.today().date().isoformat())
    send_pdf(context, template_name, subject, filename, user_pk, site_pk,
             language_code)


def export_events(extension):
    def inner(pk_list, user_pk, site_pk, language_code):
        exporter = EvenementExporter(Evenement.objects.filter(pk__in=pk_list))
        n = len(pk_list)
        subject = _('de %s événements') % n
        filename = f'{n}-evenements_{datetime.today().date().isoformat()}'
        send_export(exporter, extension, subject, filename, user_pk,
                    language_code)
    return inner


@job
def events_to_json(*args):
    export_events('json')(*args)


@job
def events_to_csv(*args):
    export_events('csv')(*args)


@job
def events_to_xlsx(*args):
    export_events('xlsx')(*args)
