#!/bin/sh

sudo apt-get install nano mysql-server python2.7 python-mysqldb python-pip python-docutils python-dev apache2 libapache2-mod-wsgi

sudo pip install django==1.3.1 django-reversion==1.5.1 django-haystack==1.2.6 django-tinymce==1.5.1a2 django-grappelli==2.3.7 django-filebrowser==3.3.0 pil django-rosetta==0.6.5 south==0.7.3 django-debug-toolbar==0.9.4 django-extensions==0.7.1

git clone git://github.com/jmacul2/django-rosetta-grappelli.git
cd django-rosetta-grappelli
git checkout 0e382426be56b7fef99624b90c9a2a72211cfff5
sudo python setup.py install
cd ..
sudo rm -r django-rosetta-grappelli

