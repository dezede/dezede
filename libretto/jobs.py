import re
from datetime import datetime
from pathlib import Path
from subprocess import Popen, check_output
from tempfile import TemporaryDirectory

from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django_rq import job
from tqdm import trange

from accounts.models import HierarchicUser
from common.utils.cache import unlock_user
from common.utils.export import send_pdf, send_export
from common.utils.file import FileAnalyzer
from libretto.export import EvenementExporter, Source, TypeDeSource
from libretto.models import Evenement


def create_image_from_pdf(pdf_path, page_index, image_path):
    p = Popen([
        'gm', 'convert',
        '-density', '300',  # Utilise une densité de 300 dpi pour assurer une
                            # haute qualité.
        '-resize', '3000x3000>',  # S’assure que la taille de l’image finale
                                  # ne dépasse pas 3000 pixels
                                  # de largeur ou hauteur.
        '-define', 'pdf:use-cropbox=true',  # Utilise la CropBox du PDF pour
                                            # déterminer les dimensions
                                            # de la partie affichée de la page.
        f'{pdf_path}[{page_index}]', image_path])
    p.wait()


def get_pdf_num_pages(path):
    return int(
        re.search(
            r'^Pages:\s+(\d+)$',
            check_output(['pdfinfo', path]).decode(),
            flags=re.MULTILINE
        ).group(1)
    )


@job
@transaction.atomic
def split_pdf(source_pk, user_pk):
    try:
        source = Source.objects.get(pk=source_pk)
        assert source.is_pdf()
        assert not source.children.exists()
        f = source.fichier
        num_pages = get_pdf_num_pages(f.path)

        with TemporaryDirectory() as tmp:
            for i in trange(num_pages):
                image_path = Path(tmp) / f'{Path(f.name).stem}_{i}.jpg'
                create_image_from_pdf(f.path, i, str(image_path))
                cf = ContentFile(image_path.read_bytes(), image_path.name)
                page = i + 1
                Source.objects.create(
                    parent=source, position=page, page=page, type=source.type,
                    fichier=cf, type_fichier=FileAnalyzer.IMAGE,
                )
    finally:
        unlock_user(HierarchicUser.objects.get(pk=user_pk))


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
