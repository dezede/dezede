#!/bin/sh

# Installe add-apt-repository.
apt-get install software-properties-common
# Ajout le dépôt PPA node.js.
add-apt-repository ppa:chris-lea/node.js
apt-get update

# Installe tous les paquets Ubuntu requis.
apt-get install nano mercurial postgresql postgresql-server-dev-9.5 python3.5 python3-pip python3.5-dev redis-server libxml2 libxml2-dev libxslt1-dev nodejs openjdk-7-jre

# Installe LESS CSS.
npm install -g less@2.5.3

# Installe le moteur de recherche elasticsearch.
wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.7.5.deb
dpkg -i elasticsearch-*.deb
rm elasticsearch-*.deb

# Pour satisfaire la construction de python-imaging (alias PIL ou Pillow)
apt-get build-dep python-imaging

# Liens symboliques pour que PIL trouve ses dépendances.
# Sans cela, Django ne peut importer que des GIF et pas de JPEG, PNG, etc.
ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/
ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/
ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/

# Installe tous les paquets python requis.
pip install -r requirements.txt
