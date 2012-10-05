'Lance solr dans un sous-processus.'
import os
import subprocess


def start():
    solr_args = ['cd apache-solr-3.6.1/example\njava -jar start.jar']
    devnull = open(os.devnull, 'wb')
    print 'Lancement de Solr...'
    return subprocess.Popen(args=solr_args,
                            stdout=devnull, stderr=devnull, shell=True)