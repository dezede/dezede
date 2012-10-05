'Lance solr dans un sous-processus.'
import os
import subprocess


def start_solr():
    solr_args = ['cd apache-solr-3.6.1/example\nkill `cat solr.pid`\n'
                 'java -Xmx50M -jar start.jar &\necho $! > solr.pid']
    devnull = open(os.devnull, 'wb')
    print 'Lancement de Solr...'
    return subprocess.Popen(args=solr_args,
                            stdout=devnull, stderr=devnull, shell=True)

if __name__ == '__main__':
    start_solr()
