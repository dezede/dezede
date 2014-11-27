# coding: utf-8

from __future__ import unicode_literals
from datetime import datetime
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage, mail_admins
from django.http import HttpRequest
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.encoding import force_text
from django_rq import job
from libretto.models import Evenement
from rq.timeouts import JobTimeoutException
from slugify import slugify
from accounts.models import HierarchicUser
from .models import DossierDEvenements
from .utils import xelatex_to_pdf, unlock_user


def get_success_mail(subject, user, filename, pdf_content):
    body = """
        <p>Bonjour,</p>

        <p>
            Vous pouvez trouver en pièce jointe l’export %s
            que vous venez de demander.
        </p>

        <p>
            Bien cordialement,<br />
            L’équipe Dezède
        </p>
    """ % subject

    mail = EmailMessage('[Dezède] Export %s' % subject,
                        body=body, to=(user.email,))
    mail.content_subtype = 'html'
    mail.attach('%s.pdf' % filename,
                pdf_content, 'application/pdf')
    return mail


def get_failure_mail(subject, user):
    body = """
        <p>Bonjour,</p>

        <p>
            L’export %s que vous venez de demander
            a échoué.  Le développeur de Dezède a été averti par mail et
            va tenter de corriger cela dans les plus brefs délais.
        </p>

        <p>
            Bien cordialement,<br />
            L’équipe Dezède
        </p>
    """ % subject

    mail = EmailMessage('[Dezède] Échec de l’export %s'
                        % subject, body=body, to=(user.email,))
    mail.content_subtype = 'html'
    return mail


def send_pdf(context, template_name, subject, filename, user_pk, site_pk,
             language_code):
    translation.activate(language_code)
    user = HierarchicUser.objects.get(pk=user_pk)
    context.update(
        user=user,
        SITE=Site.objects.get(pk=site_pk),
        source_dict={})
    request = HttpRequest()
    request.user = user
    context = RequestContext(request, context)
    try:
        tex = render_to_string(template_name, context)
    except JobTimeoutException:
        get_failure_mail(subject, user).send()
        unlock_user(user)
        raise

    try:
        pdf_content = xelatex_to_pdf(tex).read()
    except RuntimeError as e:
        mail = get_failure_mail(subject, user)
        mail_admins('Error while generating `%s`' % filename, e.body)
    else:
        mail = get_success_mail(subject, user, filename, pdf_content)

    mail.send()

    unlock_user(user)


@job
def dossier_to_pdf(dossier_pk, user_pk, site_pk, language_code):
    dossier = DossierDEvenements.objects.get(pk=dossier_pk)
    context = {'object': dossier}
    template_name = 'dossiers/dossierdevenements_detail.tex'
    subject = 'du dossier « %s »' % dossier
    filename = slugify(force_text(dossier))
    send_pdf(context, template_name, subject, filename, user_pk, site_pk,
             language_code)


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
