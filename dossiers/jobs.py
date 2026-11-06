from datetime import datetime

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django_rq import job
from slugify import slugify

from accounts.models import HierarchicUser
from common.utils.export import send_pdf, send_export

from .models import Dossier
from .export import ScenariosExporter


@job
def dossier_to_pdf(dossier_pk, user_pk, site_pk, language_code):
    dossier = Dossier.objects.get(pk=dossier_pk)
    context = {'object': dossier}
    template_name = 'dossiers/dossier_detail.tex'
    subject = _('du dossier « %s »') % dossier
    filename = slugify(str(dossier))
    send_pdf(context, template_name, subject, filename, user_pk, site_pk,
             language_code)


@job
def dossier_to_xlsx(data, user_pk, site_pk, language_code):
    dossier = Dossier.objects.get(pk=data.pop('dossier'))
    scenarios = list(filter(None, data.get('scenarios')))
    request = HttpRequest()
    request.user = HierarchicUser.objects.get(pk=user_pk)
    exporter = ScenariosExporter(dossier, scenarios, request=request)
    ids = "_".join([scenario.get('scenario').split('-')[1] for scenario in scenarios])
    subject = dossier
    filename = f'{ dossier }_scenario_{ ids }_{ datetime.today().date().isoformat()}'

    send_export(exporter, 'xlsx', subject, filename, user_pk,
                language_code)
