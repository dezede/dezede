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


#. Copier dedans le contenu de nginx/dezede.conf (en remplaçant ce qui est
   balisé ``[[quelque_chose]]``)


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
      command=gunicorn dezede.wsgi:application -w3 -t300 -b 127.0.0.1:[[port]]
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

Une suite de tests encore incomplète est disponible. Pour la lancer, exécuter :

  ``./manage.py test dezede libretto accounts dossiers typography cache_tools``



Restauration de sauvegarde SQL
==============================

| ``sudo -i -u postgres``
| ``psql -v ON_ERROR_STOP=1 dezede < dezede.sql``
