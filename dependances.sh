#!/bin/sh

apt-get install nano postgresql python2.7 python-pip python-docutils python-dev memcached libxml2

# Pour satisfaire la construction de python-imaging (alias PIL)
apt-get build-dep python-imaging

# Liens symboliques pour que PIL trouve ses dépendances.
# Sans cela, Django ne peut importer que des GIF et pas de JPEG, PNG, etc.
ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/
ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/
ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/

pip install -r requirements.txt
