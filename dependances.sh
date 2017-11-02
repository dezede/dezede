#!/bin/sh

# Installe tous les paquets Ubuntu requis.
apt-get install postgresql postgresql-server-dev-9.6 python3.6 python3-pip python3.6-dev redis-server libxml2 libxml2-dev libxslt1-dev npm default-jre elasticsearch gdal-bin postgis libav-tools texlive-xetex fonts-linuxlibertine texlive-lang-french texlive-fonts-extra

# Installe LESS CSS.
npm install

# Installe tous les paquets python requis.
pip install -r requirements.txt
