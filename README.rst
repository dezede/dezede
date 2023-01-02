*************
Projet Dezède
*************

:Auteur: Bertrand Bordage
:Copyright: Bertrand Bordage © 2011-2014

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
  Ubuntu 20.04 « Raring Ringtail »

Pour installer les dépendances qui suivent :
  ``sudo ./dependances.sh``


Paquets
-------

Nécessaires au déploiement
..........................

========== =======
Paquet     Version
========== =======
nginx      1.12.1
supervisor 3.3.1
========== =======


Clonage du projet
=================

- ``git clone https://github.com/dezede/dezede``
- ``git submodule init``
- ``git submodule update``



Configuration de PostgreSQL
===========================

.. index::
    PostgreSQL

#. Effectuer les actions suivantes :

    | ``sudo -i -u postgres``
    | ``psql``

      | ``CREATE USER dezede LOGIN CREATEDB;``
      | ``CREATE DATABASE dezede OWNER dezede;``
      | ``\q``

    | ``exit``


#. Autoriser l'utilisateur dezede à accéder à PostgreSQL par le socket unix :

   - Éditer le fichier de configuration :

        ``sudo nano /etc/postgresql/9.6/main/pg_hba.conf``

   - Ajouter cette nouvelle ligne après
     ``# Database administrative login by Unix domain socket`` :

        ::

          local dezede,test_dezede dezede trust


#. Création des tables de la base de données :

    ``./manage.py syncdb`` puis ``./manage.py migrate``


#. Redémarrer PostgreSQL :

    ``sudo systemctl restart postgresql``



Configuration de Redis
======================

#. Activer le socket Unix de Redis :

    - Éditer le fichier de configuration :

        ``sudo nano /etc/redis/redis.conf``

    - Ajouter ces lignes :

        ::

          unixsocket /var/run/redis/redis.sock
          unixsocketperm 777


#. Redémarrer Redis :

    ``sudo systemctl restart redis``



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

      [program:dezede_rq]
      directory=[[/chemin/du/projet]]
      command=python manage.py rqworker --settings=dezede.settings.prod
      user=[[utilisateur]]
      autostart=true
      autorestart=true
      redirect_stderror=true
      stdout_logfile=[[/chemin/du/projet]]/supervisor_rq.log
      stdout_logfile_maxbytes=10MB

      [group:dezede]
      programs=dezede_django,dezede_rq


#. Relancer le serveur avec :

    | ``sudo systemctl restart  supervisor``
    | ``sudo systemctl restart  nginx``



Localisation
============

#. Ajouter (éventuellement) la langue désirée à LANGUAGES du fichier settings.py

#. Télécharger l’exécutable de Transifex cli à partir de GitHub :https://github.com/transifex/cli/releases

#. Récupérer le token du projet sur https://transifex.com

#. Metre à jour à partir de Transifex :

    ``tx --hostname https://rest.api.transifex.com --token [INSÉRER_TOKEN_ICI] pull -a``

#. Compiler les fichiers de langues (en se mettant au préalable dans le
   dossier de l'application ou du projet) :

    ``./manage.py compilemessages``

#. Relancer le serveur



Tests de régression
===================

Une suite de tests encore incomplète est disponible. Pour la lancer, exécuter :

  ``./manage.py test dezede libretto accounts dossiers typography``



Restauration de sauvegarde SQL
==============================

| ``sudo -i -u postgres``
| ``psql -v ON_ERROR_STOP=1 dezede < dezede.sql``
