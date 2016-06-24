# coding: utf-8

from __future__ import unicode_literals
import io
import os
from subprocess import Popen, PIPE

from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage, mail_admins
from django.http import HttpRequest
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from rq.timeouts import JobTimeoutException

from accounts.models import HierarchicUser
from .cache import is_user_locked, lock_user, unlock_user
from .text import remove_windows_newlines


def xelatex_to_pdf(source_code):
    """
    :param source_code: XeLaTeX source
    :type source_code: unicode
    :param sleep_step: Seconds between checks whether XeLaTeX has finished
    :type sleep_step: float
    :returns: file object
    :raises ValueError: When an error is found in XeLaTeX
                        or if it takes too much time.
    """
    source_code = remove_windows_newlines(source_code)

    tmp_dir = getattr(settings, 'TMP_DIR', settings.BASE_DIR.child('tmp'))
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    tmp_filename = 'tmp.%s'
    file_abspath = os.path.join(tmp_dir, tmp_filename)
    with io.open(file_abspath % 'tex', 'w', encoding='utf-8') as f:
        f.write(source_code)

    p = Popen(['xelatex', tmp_filename % 'tex'],
              stdout=PIPE, stdin=PIPE, cwd=tmp_dir)

    try:
        out, err = p.communicate()
    except JobTimeoutException:
        p.kill()
        out = ''.join(p.stdout)

    if p.returncode:
        e = RuntimeError('Error while generating PDF using XeLaTeX.')
        e.body = out
        raise e

    return open(file_abspath % 'pdf', 'rb')


def launch_export(job, request, data, file_extension, subject):
    if is_user_locked(request.user):
        messages.error(request,
                       _('Un export de votre part est déjà en cours. '
                         'Veuillez attendre la fin de celui-ci avant d’en '
                         'lancer un autre.'))
    else:
        lock_user(request.user)
        site = Site.objects.get_current(request)
        job.delay(data, request.user.pk, site.pk, request.LANGUAGE_CODE)
        messages.info(request,
                      _('La génération de l’export %s %s est en cours. '
                        'Un courriel le contenant vous sera envoyé d’ici '
                        'quelques minutes.') % (file_extension, subject))


def get_success_mail(subject, user, filename, file_content, content_type):
    body = _("""
        <p>Bonjour,</p>

        <p>
            Vous pouvez trouver en pièce jointe l’export %s
            que vous venez de demander.
        </p>

        <p>
            Bien cordialement,<br />
            L’équipe Dezède
        </p>
    """) % subject

    mail = EmailMessage(_('[Dezède] Export %s') % subject,
                        body=body, to=(user.email,))
    mail.content_subtype = 'html'
    mail.attach(filename, file_content, content_type)
    return mail


def get_failure_mail(subject, user):
    body = _("""
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
    """) % subject

    mail = EmailMessage(_('[Dezède] Échec de l’export %s')
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
        mail = get_success_mail(subject, user, filename + '.pdf', pdf_content,
                                'application/pdf')

    mail.send()

    unlock_user(user)


def send_export(exporter_instance, extension, subject, filename, user_pk,
                language_code):
    translation.activate(language_code)
    user = HierarchicUser.objects.get(pk=user_pk)
    request = HttpRequest()
    request.user = user
    try:
        file_content = getattr(exporter_instance, 'to_' + extension)()
    except JobTimeoutException:
        get_failure_mail(subject, user).send()
        unlock_user(user)
        raise
    if isinstance(file_content, tuple):
        extension, file_content = file_content
    filename += '.' + extension
    get_success_mail(subject, user, filename, file_content,
                     exporter_instance.CONTENT_TYPES[extension]).send()
    unlock_user(user)
