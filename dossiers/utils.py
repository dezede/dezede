# coding: utf-8

from __future__ import unicode_literals
import io
from logging import getLogger
import os
from subprocess import Popen, PIPE
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import get_current_site
from django.core.cache import cache
from rq.timeouts import JobTimeoutException


logger = getLogger(__name__)


def get_user_lock_cache_key(user):
    return 'dossiers__export_en_cours__%s' % user.username


def is_user_locked(user):
    return cache.get(get_user_lock_cache_key(user), False)


def lock_user(user):
    cache.set(get_user_lock_cache_key(user), True)


def unlock_user(user):
    cache.set(get_user_lock_cache_key(user), False)


def remove_windows_newlines(text):
    return text.replace('\r\n', '\n').replace('\r', '\n')


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


def launch_pdf_export(job, request, data, subject):
    if is_user_locked(request.user):
        messages.error(request,
                       'Un export de votre part est déjà en cours. '
                       'Veuillez attendre la fin de celui-ci avant d’en '
                       'lancer un autre.')
    else:
        lock_user(request.user)
        site = get_current_site(request)
        job.delay(data, request.user.pk, site.pk, request.LANGUAGE_CODE)
        messages.info(request,
                      'La génération de l’export PDF %s '
                      'est en cours. Un courriel le contenant vous sera '
                      'envoyé d’ici quelques minutes.' % subject)
