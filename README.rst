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
  Ubuntu 12.10 « Quantal Quetzal »

Pour installer les dépendances qui suivent :
  ``sudo ./dependances.sh``


Paquets
-------

Nécessaires à l'exécution
.........................

=============== =======
Paquet          Version
=============== =======
nano
postgresql      9.1
python2.7       2.7.3
python-pip      1.1
python-docutils 0.8.1
memcached       1.4.14
python-dev      2.7.3
libxml2
libxml2-dev
libxslt1-dev
=============== =======


Nécessaires au déploiement
..........................

========== =======
Paquet     Version
========== =======
nginx      1.2.1
gunicorn   0.17.4
supervisor 3.0a8
========== =======


Modules Python
--------------

Nécessaires à l'exécution
.........................

Voir le fichier `requirements.txt`.



Configuration de PostgreSQL
===========================

.. index::
    PostgreSQL

#. Effectuer les actions suivantes :
    | ``sudo -i -u postgres``
    | ``psql``
    |   ``CREATE USER dezede LOGIN;``
    |   ``CREATE DATABASE dezede OWNER dezede;``
    |   ``ALTER USER dezede WITH ENCRYPTED PASSWORD 'mot_de_passe';``
    |   ``\q``
    | ``exit``


#. Paramétrer l'accès de Django à la base de données :
    - Éditer le fichier de réglages :
        ``nano settings.py``
    - Les réglages à modifier sont dans ``DATABASES``.


#. Création des tables de la base de données :
    ``./manage.py syncdb`` puis ``./manage.py migrate``



Lancement du serveur de développement
=====================================

#. Passer en mode ``DEBUG`` :
    - Éditer le fichier de réglages :
        ``nano settings.py``

    - Remplacer la ligne ``DEBUG = False`` par :
        ::

          DEBUG = True


#. `Configuration de PostgreSQL`_


#. Création des révisions initiales :
    ``./manage.py createinitialrevisions``


#. Collecte des fichiers statiques :
    ``./manage.py collectstatic -l``


#. Préparation du dossier d'upload :
    ``mkdir -p media/uploads/``


#. Indexation des données :
    ``./manage.py rebuild_index``


#. Lancement du serveur de développement :
    ``./manage.py runserver``



Déploiement
===========

#. `Configuration de PostgreSQL`_


#. Création des révisions initiales :
    ``./manage.py createinitialrevisions``

#. Collecte des fichiers statiques :
    ``sudo ./manage.py collectstatic``


#. Préparation du dossier d'upload :
    ``sudo mkdir -p media/uploads/``


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

      server {
        listen 80;
        server_name [[adresse_ou_domaine]];

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

        client_max_body_size 50M;

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

      [program:dezede]
      directory=[[/chemin/du/projet]]
      command=gunicorn_django
      user=www-data
      autostart=true
      autorestart=true
      redirect_stderror=true


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

  ``sudo ./manage.py test libretto``
