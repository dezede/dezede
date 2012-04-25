#!/bin/sh

sudo apt-get install nano mysql-server python2.7 python-mysqldb python-pip python-docutils python-dev apache2 libapache2-mod-wsgi

sudo pip install django==1.3.1 django-reversion==1.5.1 django-haystack==1.2.6 whoosh==2.3.2 django-tinymce==1.5.1a2 django-grappelli==2.3.7 django-filebrowser==3.3.0 pil==1.1.7 south==0.7.3 django-debug-toolbar==0.9.4 django-extensions==0.7.1

git clone git://github.com/mbi/django-rosetta.git
cd django-rosetta
git checkout e1c0fc1b18a9c406d60ea1103fadd25f21b1cef0
sudo python setup.py install
cd ..
sudo rm -r django-rosetta

git clone git://github.com/BertrandBordage/django-rosetta-grappelli.git
cd django-rosetta-grappelli
git checkout eb8f805f85674851ffc181ef46f0960241bf8638
sudo python setup.py install
cd ..
sudo rm -r django-rosetta-grappelli

