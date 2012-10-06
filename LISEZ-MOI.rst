*************
Projet Dezède
*************

:Auteur: Bertrand Bordage
:Copyright: Bertrand Bordage © 2011-2012

.. contents::


Procédure d'installation
========================

.. note::
    Toutes les commandes sont à exécuter dans le répertoire du projet.

#. Vérifier la satisfaction des `dépendances`_.

#. `Installation du moteur de recherche`_.

#. Choisir un mode de lancement :
    - `Lancement du serveur de développement`_, ou
    - `Déploiement`_.



Dépendances
===========

:Système d'exploitation:
  Ubuntu 12.04 « Precise Pangolin »

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
mysql-server    5.1
python2.7       2.7.2
python-mysqldb  1.2.3
python-pip      1.0
python-docutils 0.7
memcached       1.4.13
=============== =======


Nécessaires au déploiement
..........................

=================== =======
Paquet              Version
=================== =======
apache2             2.2
libapache2-mod-wsgi 3.3
=================== =======


Modules Python
--------------

Nécessaires à l'exécution
.........................

Voir le fichier `requirements.txt`.



Installation du moteur de recherche
===================================

#. Téléchargement d'Apache Solr :

    ``./manage.py install_solr``


#. Création du schéma pour Solr :

    ``./manage.py build_solr_schema > apache-solr-[version]/example/solr/conf/schema.xml``


#. Dans ce shéma, remplacer le fieldtype "text" par tout ceci :

    ::

      <fieldType name="text" class="solr.TextField" positionIncrementGap="100">
        <analyzer>
          <tokenizer class="solr.WhitespaceTokenizerFactory"/>
          <charFilter class="solr.MappingCharFilterFactory" mapping="mapping-ISOLatin1Accent.txt" />
          <filter class="solr.PatternReplaceFilterFactory" pattern="^(\p{Punct}*)(.*?)(\p{Punct}*)$" replacement="$2"/>
          <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_fr.txt"/>
          <filter class="solr.WordDelimiterFilterFactory" generateWordParts="1" generateNumberParts="1" catenateWords="1" catenateNumbers="1" catenateAll="0"/>
          <filter class="solr.LowerCaseFilterFactory"/>
          <filter class="solr.SnowballPorterFilterFactory" language="French"/>
        </analyzer>
      </fieldType>

      <fieldType name="textSpell" class="solr.TextField" positionIncrementGap="100">
        <analyzer>
          <tokenizer class="solr.WhitespaceTokenizerFactory"/>
          <filter class="solr.PatternReplaceFilterFactory" pattern="^(\p{Punct}*)(.*?)(\p{Punct}*)$" replacement="$2"/>
          <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_fr.txt"/>
          <filter class="solr.RemoveDuplicatesTokenFilterFactory"/>
        </analyzer>
      </fieldType>


#. Remplacer ``<field name="suggestions" type="text"`` par
   ``<field name="suggestions" type="textSpell"``


#. Changer le port dans le fichier `apache-sorl-[version]/example/etc/jetty.xml`


#. Ajouter ceci dans le tag *config* du fichier
   ``apache-sorl-[version]/example/solr/conf/solrconfig.xml`` :

    ::

      <requestHandler name="/mlt" class="solr.MoreLikeThisHandler" />
      <searchComponent name="spellcheck" class="solr.SpellCheckComponent">
        <str name="queryAnalyzerFieldType">textSpell</str>
        <lst name="spellchecker">
          <str name="name">default</str>
          <str name="field">suggestions</str>
          <str name="spellcheckIndexDir">./spellchecker1</str>
          <str name="buildOnCommit">true</str>
        </lst>
      </searchComponent>


#. Ajouter ceci au tag
   ``<requestHandler name="/select" class="solr.SearchHandler">`` :

    ::

      <arr name="last-components">
        <str>spellcheck</str>
      </arr>


#. Pour lancer Solr, lancer :

    ``python dezede/solr.py``



Configuration de MySQL
======================

.. index::
    MySQL

#. Création de la base de données dans MySQL :
    ``mysql -uroot -p``
    ::

      CREATE DATABASE criminocorpus;
      exit;


#. Paramétrer l'authentification de MySQL :

    - Éditer le fichier de réglages :
        ``nano settings.py``
    - Les réglages à modifier sont dans ``DATABASES``.


#. Création des tables de la base de données :
    ``./manage.py syncdb``



Lancement du serveur de développement
=====================================

#. Passer en mode ``DEBUG`` :
    - Éditer le fichier de réglages :
        ``nano settings.py``

    - Remplacer la ligne ``DEBUG = False`` par :
        ::

          DEBUG = True


#. `Configuration de MySQL`_


#. Création des révisions initiales :
    ``./manage.py createinitialrevisions``


#. Collecte des fichiers statiques :
    ``./manage.py collectstatic -l``


#. Préparation du dossier d'upload :
    ``mkdir -p media/uploads/``


#. Compiler les fichiers de langues :
    ``./manage.py compilemessages``


#. Indexation des données :
    ``./manage.py rebuild_index``


#. Lancement du serveur de développement :
    ``./manage.py runserver``



Déploiement
===========

#. `Configuration de MySQL`_


#. Création des révisions initiales :
    ``./manage.py createinitialrevisions``


#. Collecte des fichiers statiques :
    ``./manage.py collectstatic``


#. Préparation du dossier d'upload :
    ``mkdir -p media/uploads/``


#. Autoriser les uploads :
    | ``sudo chgrp -R www-data /media/``
    | ``sudo chmod -R 0774 /media/``


#. Compiler les fichiers de langues :
    ``./manage.py compilemessages``


#. Indexation des données :
    ``./manage.py rebuild_index``


#. Autoriser apache à utiliser le dossier où se trouve le projet :
    | ``sudo chgrp -R www-data
        [/chemin/vers/le/repertoire/parent/de/celui/du/projet]``
    | ``sudo chmod -R 0774
        [/chemin/vers/le/repertoire/parent/de/celui/du/projet]``


#. `Configuration d'Apache`_



Configuration d'Apache
======================

.. index::
    Apache

#. Création d'un site dans Apache :
    ``sudo nano /etc/apache2/sites-available/dezede``


#. Copier ceci dans ce dernier (en remplaçant ce qui est balisé ``[quelque_chose]``) :
    ::

      <VirtualHost *:80>

        Alias /media/ [/chemin/du/projet]/media/
        Alias /static/ [/chemin/du/projet]/static/

        <Directory [/chemin/du/projet]/media>
          Order deny,allow
          Allow from all
          Options FollowSymLinks
          ExpiresActive On
          ExpiresDefault "access plus 2 days"
        </Directory>

        <Directory [/chemin/du/projet]/static>
          Order deny,allow
          Allow from all
          Options FollowSymLinks
          ExpiresActive On
          ExpiresDefault "access plus 2 days"
        </Directory>

        WSGIScriptAlias / [/chemin/du/projet]/apache/django.wsgi

        <Directory [/chemin/du/projet]/apache>
          Order deny,allow
          Allow from all
        </Directory>

      </VirtualHost>

    .. note::
        On peut ajouter le paramètre ``MaxRequestsPerChild 1``
        avant ``<VirtualHost ...>`` pour éviter d'avoir à relancer
        le serveur à chaque modification.

#. Ajouter le nom de serveur à ``/etc/apache2/httpd.conf`` :
    ::

      ServerName [ip_du_serveur]


#. Activer le site et désactiver le site par défaut :
    | ``sudo a2ensite dezede``
    | ``sudo a2dissite default``


#. Activer l'expiration du cache :
    ``sudo a2enmod expires``


#. Relancer le serveur avec :
    ``sudo service apache2 restart``



Localisation
============

#. Ajouter (éventuellement) la langue désirée à LANGUAGES du fichier settings.py

#. Créer ou mettre à jour le fichier de langue désirée :
    ``sudo ./manage.py makemessages -l [langue (ex : de)]``

#. Éditer le fichier de langue :
    ``nano locale/[langue]/LC_MESSAGES/django.po``

#. Compiler les fichiers de langues :
    ``./manage.py compilemessages``

#. Relancer le serveur



Tests de régression
===================

Une suite de tests a été créée pour l’application catalogue.
Pour la lancer, exécuter :

  ``sudo ./manage.py test catalogue``
