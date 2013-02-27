# coding: utf-8

from __future__ import unicode_literals
from django.core.management.base import BaseCommand
import os
import tarfile


class Command(BaseCommand):
    help = 'Télécharge et installe Apache Solr'

    def handle(self, *args, **options):
        version = '3.6.1'
        filename = 'apache-solr-%s.tgz' % version
        repository = 'ftp://mirrors.ircam.fr/pub/apache/lucene/solr'

        if not os.path.exists(filename):
            fullurl = os.path.join(repository, version, filename)
            print('Téléchargement de Solr version %s en cours...' % version)
            print('(Pour suivre son déroulement, '
                  'lisez le fichier download.log.)')
            os.system('wget %s -a download.log' % fullurl)
        else:
            print('Fichier %s trouvé.' % filename)

        print('Extraction en cours...')
        tar = tarfile.open(filename)
        tar.extractall()
