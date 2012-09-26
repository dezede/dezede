#!/bin/sh

apt-get install nano mysql-server python2.7 python-mysqldb python-pip python-docutils python-dev apache2 libapache2-mod-wsgi memcached

pip install -r requirements.txt

git clone git://github.com/mbi/django-rosetta.git
cd django-rosetta
git checkout e1c0fc1b18a9c406d60ea1103fadd25f21b1cef0
python setup.py install
cd ..
rm -rf django-rosetta

git clone git://github.com/jmacul2/django-rosetta-grappelli.git
cd django-rosetta-grappelli
git checkout 7e715c3de31b8db4396d331816d11c1bb5746020
python setup.py install
cd ..
rm -rf django-rosetta-grappelli
