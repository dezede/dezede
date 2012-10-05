# coding: utf-8

from django.core.management.base import BaseCommand, CommandError
import os
import tarfile


class Command(BaseCommand):
    help = u'Télécharge et installe Apache Solr'

    def handle(self, *args, **options):
        version = '3.6.1'
        filename = 'apache-solr-%s.tgz' % version
        repository = 'ftp://mirrors.ircam.fr/pub/apache/lucene/solr'

        if not os.path.exists(filename):
            fullurl = os.path.join(repository, version, filename)
            print u'Téléchargement de Solr version %s en cours...' % version
            print u'(Pour suivre son déroulement, lisez le fichier download.log.)'
            os.system('wget %s -a download.log' % fullurl)
        else:
            print 'Fichier %s trouvé.' % filename

        print 'Extraction en cours...'
        tar = tarfile.open(filename, 'r')
        tar.extractall()
