from datetime import datetime

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django_rq import job
from slugify import slugify

from common.utils.export import send_pdf, send_export

from .models import Dossier
from .export import ScenariosExporter


@job
def dossier_to_pdf(dossier_pk, user_pk, site_pk, language_code):
    dossier = Dossier.objects.get(pk=dossier_pk).specific
    context = {'object': dossier}
    template_name = f'dossiers/{dossier._meta.model_name}_detail.tex'
    subject = _('du dossier « %s »') % dossier
    filename = slugify(force_text(dossier))
    send_pdf(context, template_name, subject, filename, user_pk, site_pk,
             language_code)


@job
def dossier_to_xlsx(data, user_pk, site_pk, language_code):
    dossier = Dossier.objects.get(pk=data.pop('dossier')).specific
    scenarios = list(filter(None, data.get('scenarios')))
    exporter = ScenariosExporter(dossier, scenarios)
    ids = "_".join([scenario.get('scenario').split('-')[1] for scenario in scenarios])
    subject = dossier
    filename = f'{ dossier }_scenario_{ ids }_{ datetime.today().date().isoformat()}'

    send_export(exporter, 'xlsx', subject, filename, user_pk,
                language_code)
