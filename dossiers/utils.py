# coding: utf-8

from __future__ import unicode_literals
import io
from logging import getLogger
import os
from subprocess import Popen, PIPE
from time import sleep
from django.conf import settings
from rq.timeouts import JobTimeoutException


logger = getLogger(__name__)


def get_user_limit_cache_key(user):
    return 'dossiers__export_en_cours__%s' % user.username


def remove_windows_newlines(text):
    return text.replace('\r\n', '\n').replace('\r', '\n')


def xelatex_to_pdf(source_code, sleep_step=0.05):
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

    p = Popen(['xelatex', tmp_filename % 'tex'], stdout=PIPE, cwd=tmp_dir)

    try:
        while True:
            sleep(sleep_step)
            p.communicate()
            if p.poll() is not None:
                break
    except JobTimeoutException:
        p.kill()
        logger.error(''.join(p.stdout))
        raise ValueError('Error while generating PDF using XeLaTeX.')

    return open(file_abspath % 'pdf', 'rb')
