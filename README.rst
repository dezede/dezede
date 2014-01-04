*************
Projet Dezède
*************

:Auteur: Bertrand Bordage
:Copyright: Bertrand Bordage © 2011-2013

|travis|_
|coveralls|_

.. |travis| image:: https://travis-ci.org/dezede/dezede.png
.. _travis: https://travis-ci.org/dezede/dezede

.. |coveralls| image:: https://coveralls.io/repos/dezede/dezede/badge.png
.. _coveralls: https://coveralls.io/r/dezede/dezede

.. contents::


Procédure d'installation
========================

.. note::
    Toutes les commandes sont à exécuter dans le répertoire du projet.

#. Vérifier la satisfaction des `dépendances`_.

#. Choisir un mode de lancement :
    - `Lancement du serveur de développement`_, ou
    - `Déploiement`_.



Dépendances
===========

:Système d'exploitation:
  Ubuntu 13.04 « Raring Ringtail »

Pour installer les dépendances qui suivent :
  ``sudo ./dependances.sh``


Paquets
-------

Nécessaires à l'exécution
.........................

========================= =======
Paquet Ubuntu             Version
========================= =======
nano
mercurial
postgresql                9.1
postgresql-server-dev-9.1
python2.7                 2.7.4
python-pip                1.3.1
redis-server              2:2.6.7
python-dev                2.7.4
libxml2
libxml2-dev
libxslt1-dev
openjdk-7-jre
elasticsearch             0.90.7
rabbitmq-server           3.0.2
nodejs                    0.10.22
========================= =======

================= =======
Module javascript Version
================= =======
less              1.5.0
================= =======


Nécessaires au déploiement
..........................

========== =======
Paquet     Version
========== =======
nginx      1.2.6
supervisor 3.0a8
========== =======



Configuration de PostgreSQL
===========================

.. index::
    PostgreSQL

#. Effectuer les actions suivantes :

    | ``sudo -i -u postgres``
    | ``psql``

      | ``CREATE USER dezede LOGIN;``
      | ``CREATE DATABASE dezede OWNER dezede;``
      | ``\q``

    | ``exit``


#. Autoriser l'utilisateur dezede à accéder à PostgreSQL par le socket unix :

   - Éditer le fichier de configuration :

        ``sudo nano /etc/postgresql/9.1/main/pg_hba.conf``

   - Ajouter cette ligne :

        ::

          local dezede dezede trust


#. Création des tables de la base de données :

    ``./manage.py syncdb`` puis ``./manage.py migrate``



Configuration de Redis
======================

#. Activer le socket Unix de Redis :

    - Éditer le fichier de configuration :

        ``sudo nano /etc/redis/redis.conf``

    - Ajouter ces lignes :

        ::

          unixsocket /var/run/redis/redis.sock
          unixsocketperm 777


#. Relancer le serveur :

    ``sudo service redis-server restart``



Lancement du serveur de développement
=====================================

#. `Configuration de PostgreSQL`_


#. `Configuration de Redis`_


#. Création des révisions initiales :

    ``./manage.py createinitialrevisions``


#. Collecte des fichiers statiques :

    ``./manage.py collectstatic -l``


#. Préparation du dossier d'upload :

    ``mkdir -p media/uploads/``


#. Indexation des données :

    ``./manage.py rebuild_index``


#. Lancement du serveur de développement :

    ``DJANGO_DEBUG=True ./manage.py runserver``



Déploiement
===========

#. `Configuration de PostgreSQL`_


#. `Configuration de Redis`_


#. Création des révisions initiales :

    ``./manage.py createinitialrevisions``

#. Collecte des fichiers statiques :

    ``./manage.py collectstatic``


#. Préparation du dossier d'upload :

    ``mkdir -p media/uploads/``


#. Compiler les fichiers de langues :

    ``./manage.py compilemessages``


#. Indexation des données :

    ``./manage.py rebuild_index``


#. `Configuration de nginx`_



Configuration de nginx
======================

.. index::
    nginx

#. Création d'un site dans nginx :

    ``sudo nano /etc/nginx/sites-available/dezede``


#. Copier ceci dans ce dernier (en remplaçant ce qui est balisé
   ``[[quelque_chose]]``) :

    ::

      # Don't show infos about the server on error pages
      server_tokens off;

      # Zones created to avoid DDOS attacks
      limit_conn_zone $binary_remote_addr zone=dezede_django_conn:1m;
      limit_req_zone $binary_remote_addr zone=dezede_django_req:1m rate=3r/s;
      limit_conn_zone $binary_remote_addr zone=dezede_static_conn:10m;
      limit_req_zone $binary_remote_addr zone=dezede_static_req:10m rate=50r/s;

      server {
        listen 80;
        server_name [[adresse_ou_domaine]];
        rewrite ^(.*) https://$host$1 permanent;
      }

      server {
        listen 443 ssl;
        server_name [[adresse_ou_domaine]];
        ssl_certificate     [[/chemin/du/certificat.crt]];
        ssl_certificate_key [[/chemin/de/la/clé.key]];

        error_page 403 404 =404 /404;

        gzip on;
        gzip_vary on;
        gzip_types
          text/plain
          text/css
          text/javascript
          application/x-javascript
          image/png
          image/svg+xml
          image/jpeg
          image/x-icon
          application/pdf
          application/octet-stream;

        add_header Cache-Control public;
        # HSTS
        add_header Strict-Transport-Security "max-age=86400; includeSubdomains";
        # Clickjacking protection
        add_header X-Frame-Options SAMEORIGIN;
        # Disables browser content-type sniffing
        add_header X-Content-Type-Options nosniff;
        # Enables cross-site scripting protection
        add_header X-XSS-Protection "1; mode=block";

        client_max_body_size 50M;

        limit_conn dezede_static_conn 50;
        limit_req zone=dezede_static_req burst=500;

        location /media {
          alias [[/chemin/du/projet]]/media;
          allow all;
          expires 1y;
        }

        location /static {
          alias [[/chemin/du/projet]]/static;
          allow all;
          expires 1w;
        }

        location / {
          proxy_pass http://localhost:8000;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header Host $http_host;
          proxy_redirect off;
          proxy_connect_timeout 300s;
          proxy_read_timeout 300s;
          # Parameters to avoid DDOS attacks
          limit_conn dezede_django_conn 3;
          limit_req zone=dezede_django_req burst=20;
        }
      }


#. Activer le site et désactiver le site par défaut :

    | ``sudo ln -s /etc/nginx/sites-available/dezede
      /etc/nginx/sites-enabled/``
    | ``sudo unlink /etc/nginx/sites-enabled/default``


#. Configuration de supervisor pour lancer automatiquement le serveur django
   avec gunicorn :

    ``sudo nano /etc/supervisor/conf.d/dezede.conf``


#. Copier ceci dans ce dernier (en remplaçant ce qui est balisé
   ``[[quelque_chose]]``) :

    ::

      [program:dezede_django]
      directory=[[/chemin/du/projet]]
      command=gunicorn dezede.wsgi:application -w3 -t300 -b [[ip]]:[[port]]
      user=[[utilisateur]]
      autostart=true
      autorestart=true
      redirect_stderror=true
      stdout_logfile=[[/chemin/du/projet]]/supervisor_django.log
      stdout_logfile_maxbytes=10MB

      [program:dezede_celery]
      directory=[[/chemin/du/projet]]
      command=celery -A dezede worker
      user=[[utilisateur]]
      autostart=true
      autorestart=true
      redirect_stderror=true
      stdout_logfile=[[/chemin/du/projet]]/supervisor_celery.log
      stdout_logfile_maxbytes=10MB

      [group:dezede]
      programs=dezede_django,dezede_celery


#. Relancer le serveur avec :

    | ``sudo service supervisor restart``
    | ``sudo service nginx restart``



Localisation
============

#. Ajouter (éventuellement) la langue désirée à LANGUAGES du fichier settings.py

#. Metre à jour à partir de Transifex :

    ``tx pull -a``

#. Compiler les fichiers de langues (en se mettant au préalable dans le
   dossier de l'application ou du projet) :

    ``./manage.py compilemessages``

#. Relancer le serveur



Tests de régression
===================

Une suite de tests a été créée pour l’application libretto.
Pour la lancer, exécuter :

  ``./manage.py test dezede libretto accounts dossiers typography cache_tools``



Restauration de sauvegarde SQL
==============================

| ``sudo -i -u postgres``
| ``psql -v ON_ERROR_STOP=1 dezede < dezede.sql``
