# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'TypeDeSource', fields ['nom']
        db.create_index(u'catalogue_typedesource', ['nom'])

        # Adding index on 'TypeDeSource', fields ['nom_pluriel']
        db.create_index(u'catalogue_typedesource', ['nom_pluriel'])

        # Adding index on 'TypeDePersonnel', fields ['nom']
        db.create_index(u'catalogue_typedepersonnel', ['nom'])

        # Adding index on 'Profession', fields ['nom']
        db.create_index(u'catalogue_profession', ['nom'])

        # Adding index on 'CaracteristiqueDOeuvre', fields ['classement']
        db.create_index(u'catalogue_caracteristiquedoeuvre', ['classement'])

        # Adding index on 'NatureDeLieu', fields ['nom']
        db.create_index(u'catalogue_naturedelieu', ['nom'])

        # Adding index on 'NatureDeLieu', fields ['referent']
        db.create_index(u'catalogue_naturedelieu', ['referent'])

        # Adding index on 'Prenom', fields ['prenom']
        db.create_index(u'catalogue_prenom', ['prenom'])

        # Adding index on 'Prenom', fields ['favori']
        db.create_index(u'catalogue_prenom', ['favori'])

        # Adding index on 'Prenom', fields ['classement']
        db.create_index(u'catalogue_prenom', ['classement'])

        # Adding index on 'Pupitre', fields ['quantite_max']
        db.create_index(u'catalogue_pupitre', ['quantite_max'])

        # Adding index on 'Pupitre', fields ['quantite_min']
        db.create_index(u'catalogue_pupitre', ['quantite_min'])

        # Adding index on 'ElementDeProgramme', fields ['autre']
        db.create_index(u'catalogue_elementdeprogramme', ['autre'])

        # Adding index on 'TypeDeParenteDOeuvres', fields ['nom']
        db.create_index(u'catalogue_typedeparentedoeuvres', ['nom'])

        # Adding index on 'TypeDeParenteDOeuvres', fields ['classement']
        db.create_index(u'catalogue_typedeparentedoeuvres', ['classement'])

        # Adding index on 'TypeDeParenteDOeuvres', fields ['nom_relatif']
        db.create_index(u'catalogue_typedeparentedoeuvres', ['nom_relatif'])

        # Adding index on 'Partie', fields ['nom']
        db.create_index(u'catalogue_partie', ['nom'])

        # Adding index on 'Partie', fields ['classement']
        db.create_index(u'catalogue_partie', ['classement'])

        # Adding index on 'Source', fields ['nom']
        db.create_index(u'catalogue_source', ['nom'])

        # Adding index on 'Source', fields ['numero']
        db.create_index(u'catalogue_source', ['numero'])

        # Adding index on 'Source', fields ['date']
        db.create_index(u'catalogue_source', ['date'])

        # Adding index on 'Devise', fields ['nom']
        db.create_index(u'catalogue_devise', ['nom'])

        # Adding index on 'Devise', fields ['symbole']
        db.create_index(u'catalogue_devise', ['symbole'])

        # Adding index on 'TypeDeCaracteristiqueDOeuvre', fields ['nom']
        db.create_index(u'catalogue_typedecaracteristiquedoeuvre', ['nom'])

        # Adding index on 'CaracteristiqueDElementDeProgramme', fields ['nom']
        db.create_index(u'catalogue_caracteristiquedelementdeprogramme', ['nom'])

        # Adding index on 'CaracteristiqueDElementDeProgramme', fields ['classement']
        db.create_index(u'catalogue_caracteristiquedelementdeprogramme', ['classement'])

        # Adding index on 'Individu', fields ['nom']
        db.create_index(u'catalogue_individu', ['nom'])

        # Adding index on 'Individu', fields ['particule_nom']
        db.create_index(u'catalogue_individu', ['particule_nom'])

        # Adding index on 'Individu', fields ['particule_nom_naissance']
        db.create_index(u'catalogue_individu', ['particule_nom_naissance'])

        # Adding index on 'Individu', fields ['pseudonyme']
        db.create_index(u'catalogue_individu', ['pseudonyme'])

        # Adding index on 'Individu', fields ['titre']
        db.create_index(u'catalogue_individu', ['titre'])

        # Adding index on 'Individu', fields ['nom_naissance']
        db.create_index(u'catalogue_individu', ['nom_naissance'])

        # Adding index on 'Engagement', fields ['salaire']
        db.create_index(u'catalogue_engagement', ['salaire'])

        # Adding index on 'Oeuvre', fields ['prefixe_titre']
        db.create_index(u'catalogue_oeuvre', ['prefixe_titre'])

        # Adding index on 'Oeuvre', fields ['titre']
        db.create_index(u'catalogue_oeuvre', ['titre'])

        # Adding index on 'Oeuvre', fields ['titre_secondaire']
        db.create_index(u'catalogue_oeuvre', ['titre_secondaire'])

        # Adding index on 'Oeuvre', fields ['prefixe_titre_secondaire']
        db.create_index(u'catalogue_oeuvre', ['prefixe_titre_secondaire'])

        # Adding index on 'Oeuvre', fields ['coordination']
        db.create_index(u'catalogue_oeuvre', ['coordination'])

        # Adding index on 'Lieu', fields ['nom']
        db.create_index(u'catalogue_lieu', ['nom'])

        # Adding index on 'GenreDOeuvre', fields ['nom']
        db.create_index(u'catalogue_genredoeuvre', ['nom'])

        # Adding index on 'GenreDOeuvre', fields ['referent']
        db.create_index(u'catalogue_genredoeuvre', ['referent'])

        # Adding index on 'TypeDeParenteDIndividus', fields ['nom']
        db.create_index(u'catalogue_typedeparentedindividus', ['nom'])

        # Adding index on 'TypeDeParenteDIndividus', fields ['classement']
        db.create_index(u'catalogue_typedeparentedindividus', ['classement'])

        # Adding index on 'Evenement', fields ['relache']
        db.create_index(u'catalogue_evenement', ['relache'])

        # Adding index on 'Evenement', fields ['circonstance']
        db.create_index(u'catalogue_evenement', ['circonstance'])

        # Adding index on 'Auteur', fields ['object_id']
        db.create_index(u'catalogue_auteur', ['object_id'])

        # Adding index on 'AncrageSpatioTemporel', fields ['heure']
        db.create_index(u'catalogue_ancragespatiotemporel', ['heure'])

        # Adding index on 'AncrageSpatioTemporel', fields ['lieu_approx']
        db.create_index(u'catalogue_ancragespatiotemporel', ['lieu_approx'])

        # Adding index on 'AncrageSpatioTemporel', fields ['date_approx']
        db.create_index(u'catalogue_ancragespatiotemporel', ['date_approx'])

        # Adding index on 'AncrageSpatioTemporel', fields ['date']
        db.create_index(u'catalogue_ancragespatiotemporel', ['date'])

        # Adding index on 'AncrageSpatioTemporel', fields ['heure_approx']
        db.create_index(u'catalogue_ancragespatiotemporel', ['heure_approx'])


    def backwards(self, orm):
        # Removing index on 'AncrageSpatioTemporel', fields ['heure_approx']
        db.delete_index(u'catalogue_ancragespatiotemporel', ['heure_approx'])

        # Removing index on 'AncrageSpatioTemporel', fields ['date']
        db.delete_index(u'catalogue_ancragespatiotemporel', ['date'])

        # Removing index on 'AncrageSpatioTemporel', fields ['date_approx']
        db.delete_index(u'catalogue_ancragespatiotemporel', ['date_approx'])

        # Removing index on 'AncrageSpatioTemporel', fields ['lieu_approx']
        db.delete_index(u'catalogue_ancragespatiotemporel', ['lieu_approx'])

        # Removing index on 'AncrageSpatioTemporel', fields ['heure']
        db.delete_index(u'catalogue_ancragespatiotemporel', ['heure'])

        # Removing index on 'Auteur', fields ['object_id']
        db.delete_index(u'catalogue_auteur', ['object_id'])

        # Removing index on 'Evenement', fields ['circonstance']
        db.delete_index(u'catalogue_evenement', ['circonstance'])

        # Removing index on 'Evenement', fields ['relache']
        db.delete_index(u'catalogue_evenement', ['relache'])

        # Removing index on 'TypeDeParenteDIndividus', fields ['classement']
        db.delete_index(u'catalogue_typedeparentedindividus', ['classement'])

        # Removing index on 'TypeDeParenteDIndividus', fields ['nom']
        db.delete_index(u'catalogue_typedeparentedindividus', ['nom'])

        # Removing index on 'GenreDOeuvre', fields ['referent']
        db.delete_index(u'catalogue_genredoeuvre', ['referent'])

        # Removing index on 'GenreDOeuvre', fields ['nom']
        db.delete_index(u'catalogue_genredoeuvre', ['nom'])

        # Removing index on 'Lieu', fields ['nom']
        db.delete_index(u'catalogue_lieu', ['nom'])

        # Removing index on 'Oeuvre', fields ['coordination']
        db.delete_index(u'catalogue_oeuvre', ['coordination'])

        # Removing index on 'Oeuvre', fields ['prefixe_titre_secondaire']
        db.delete_index(u'catalogue_oeuvre', ['prefixe_titre_secondaire'])

        # Removing index on 'Oeuvre', fields ['titre_secondaire']
        db.delete_index(u'catalogue_oeuvre', ['titre_secondaire'])

        # Removing index on 'Oeuvre', fields ['titre']
        db.delete_index(u'catalogue_oeuvre', ['titre'])

        # Removing index on 'Oeuvre', fields ['prefixe_titre']
        db.delete_index(u'catalogue_oeuvre', ['prefixe_titre'])

        # Removing index on 'Engagement', fields ['salaire']
        db.delete_index(u'catalogue_engagement', ['salaire'])

        # Removing index on 'Individu', fields ['nom_naissance']
        db.delete_index(u'catalogue_individu', ['nom_naissance'])

        # Removing index on 'Individu', fields ['titre']
        db.delete_index(u'catalogue_individu', ['titre'])

        # Removing index on 'Individu', fields ['pseudonyme']
        db.delete_index(u'catalogue_individu', ['pseudonyme'])

        # Removing index on 'Individu', fields ['particule_nom_naissance']
        db.delete_index(u'catalogue_individu', ['particule_nom_naissance'])

        # Removing index on 'Individu', fields ['particule_nom']
        db.delete_index(u'catalogue_individu', ['particule_nom'])

        # Removing index on 'Individu', fields ['nom']
        db.delete_index(u'catalogue_individu', ['nom'])

        # Removing index on 'CaracteristiqueDElementDeProgramme', fields ['classement']
        db.delete_index(u'catalogue_caracteristiquedelementdeprogramme', ['classement'])

        # Removing index on 'CaracteristiqueDElementDeProgramme', fields ['nom']
        db.delete_index(u'catalogue_caracteristiquedelementdeprogramme', ['nom'])

        # Removing index on 'TypeDeCaracteristiqueDOeuvre', fields ['nom']
        db.delete_index(u'catalogue_typedecaracteristiquedoeuvre', ['nom'])

        # Removing index on 'Devise', fields ['symbole']
        db.delete_index(u'catalogue_devise', ['symbole'])

        # Removing index on 'Devise', fields ['nom']
        db.delete_index(u'catalogue_devise', ['nom'])

        # Removing index on 'Source', fields ['date']
        db.delete_index(u'catalogue_source', ['date'])

        # Removing index on 'Source', fields ['numero']
        db.delete_index(u'catalogue_source', ['numero'])

        # Removing index on 'Source', fields ['nom']
        db.delete_index(u'catalogue_source', ['nom'])

        # Removing index on 'Partie', fields ['classement']
        db.delete_index(u'catalogue_partie', ['classement'])

        # Removing index on 'Partie', fields ['nom']
        db.delete_index(u'catalogue_partie', ['nom'])

        # Removing index on 'TypeDeParenteDOeuvres', fields ['nom_relatif']
        db.delete_index(u'catalogue_typedeparentedoeuvres', ['nom_relatif'])

        # Removing index on 'TypeDeParenteDOeuvres', fields ['classement']
        db.delete_index(u'catalogue_typedeparentedoeuvres', ['classement'])

        # Removing index on 'TypeDeParenteDOeuvres', fields ['nom']
        db.delete_index(u'catalogue_typedeparentedoeuvres', ['nom'])

        # Removing index on 'ElementDeProgramme', fields ['autre']
        db.delete_index(u'catalogue_elementdeprogramme', ['autre'])

        # Removing index on 'Pupitre', fields ['quantite_min']
        db.delete_index(u'catalogue_pupitre', ['quantite_min'])

        # Removing index on 'Pupitre', fields ['quantite_max']
        db.delete_index(u'catalogue_pupitre', ['quantite_max'])

        # Removing index on 'Prenom', fields ['classement']
        db.delete_index(u'catalogue_prenom', ['classement'])

        # Removing index on 'Prenom', fields ['favori']
        db.delete_index(u'catalogue_prenom', ['favori'])

        # Removing index on 'Prenom', fields ['prenom']
        db.delete_index(u'catalogue_prenom', ['prenom'])

        # Removing index on 'NatureDeLieu', fields ['referent']
        db.delete_index(u'catalogue_naturedelieu', ['referent'])

        # Removing index on 'NatureDeLieu', fields ['nom']
        db.delete_index(u'catalogue_naturedelieu', ['nom'])

        # Removing index on 'CaracteristiqueDOeuvre', fields ['classement']
        db.delete_index(u'catalogue_caracteristiquedoeuvre', ['classement'])

        # Removing index on 'Profession', fields ['nom']
        db.delete_index(u'catalogue_profession', ['nom'])

        # Removing index on 'TypeDePersonnel', fields ['nom']
        db.delete_index(u'catalogue_typedepersonnel', ['nom'])

        # Removing index on 'TypeDeSource', fields ['nom_pluriel']
        db.delete_index(u'catalogue_typedesource', ['nom_pluriel'])

        # Removing index on 'TypeDeSource', fields ['nom']
        db.delete_index(u'catalogue_typedesource', ['nom'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'catalogue.ancragespatiotemporel': {
            'Meta': {'ordering': "[u'date', u'heure', u'lieu__parent', u'lieu', u'date_approx', u'heure_approx', u'lieu_approx']", 'object_name': 'AncrageSpatioTemporel'},
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'date_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'heure': ('django.db.models.fields.TimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'heure_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lieu': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'ancrages'", 'null': 'True', 'to': u"orm['catalogue.Lieu']"}),
            'lieu_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.auteur': {
            'Meta': {'ordering': "[u'profession', u'individu__nom']", 'object_name': 'Auteur'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individu': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'auteurs'", 'to': u"orm['catalogue.Individu']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'auteurs'", 'to': u"orm['catalogue.Profession']"})
        },
        u'catalogue.caracteristiquedelementdeprogramme': {
            'Meta': {'ordering': "[u'nom']", 'object_name': 'CaracteristiqueDElementDeProgramme'},
            'classement': ('django.db.models.fields.FloatField', [], {'default': '1.0', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '110', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.caracteristiquedoeuvre': {
            'Meta': {'ordering': "(u'type', u'classement', u'valeur')", 'object_name': 'CaracteristiqueDOeuvre'},
            'classement': ('django.db.models.fields.FloatField', [], {'default': '1.0', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'caracteristiques_d_oeuvre'", 'to': u"orm['catalogue.TypeDeCaracteristiqueDOeuvre']"}),
            'valeur': ('django.db.models.fields.CharField', [], {'max_length': '400'})
        },
        u'catalogue.devise': {
            'Meta': {'object_name': 'Devise'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '200', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'symbole': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10', 'db_index': 'True'})
        },
        u'catalogue.document': {
            'Meta': {'ordering': "[u'document']", 'object_name': 'Document'},
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'document': ('filebrowser.fields.FileBrowseField', [], {'max_length': '400'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.elementdedistribution': {
            'Meta': {'ordering': "[u'pupitre']", 'object_name': 'ElementDeDistribution'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individus': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'elements_de_distribution'", 'symmetrical': 'False', 'to': u"orm['catalogue.Individu']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_distribution'", 'null': 'True', 'to': u"orm['catalogue.Profession']"}),
            'pupitre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_distribution'", 'null': 'True', 'to': u"orm['catalogue.Pupitre']"})
        },
        u'catalogue.elementdeprogramme': {
            'Meta': {'ordering': "(u'position', u'oeuvre')", 'object_name': 'ElementDeProgramme'},
            'autre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '500', 'blank': 'True'}),
            'caracteristiques': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['catalogue.CaracteristiqueDElementDeProgramme']"}),
            'distribution': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['catalogue.ElementDeDistribution']"}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'blank': 'True'}),
            'evenement': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'programme'", 'to': u"orm['catalogue.Evenement']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'numerotation': ('django.db.models.fields.CharField', [], {'default': "u'O'", 'max_length': '1'}),
            'oeuvre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'to': u"orm['catalogue.Oeuvre']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'personnels': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['catalogue.Personnel']"}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'catalogue.engagement': {
            'Meta': {'object_name': 'Engagement'},
            'devise': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'engagements'", 'null': 'True', 'to': u"orm['catalogue.Devise']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individus': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'engagements'", 'symmetrical': 'False', 'to': u"orm['catalogue.Individu']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'engagements'", 'to': u"orm['catalogue.Profession']"}),
            'salaire': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.etat': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'Etat'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'nom'"})
        },
        u'catalogue.evenement': {
            'Meta': {'ordering': "(u'ancrage_debut',)", 'object_name': 'Evenement'},
            'ancrage_debut': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'evenements_debuts'", 'unique': 'True', 'to': u"orm['catalogue.AncrageSpatioTemporel']"}),
            'ancrage_fin': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "u'evenements_fins'", 'unique': 'True', 'null': 'True', 'to': u"orm['catalogue.AncrageSpatioTemporel']"}),
            'circonstance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '500', 'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'relache': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'})
        },
        u'catalogue.genredoeuvre': {
            'Meta': {'ordering': "[u'slug']", 'object_name': 'GenreDOeuvre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '430', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'enfants'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['catalogue.GenreDOeuvre']"}),
            'referent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'get_slug'"})
        },
        u'catalogue.illustration': {
            'Meta': {'ordering': "[u'image']", 'object_name': 'Illustration'},
            'commentaire': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('filebrowser.fields.FileBrowseField', [], {'max_length': '400'}),
            'legende': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.individu': {
            'Meta': {'ordering': "(u'nom',)", 'object_name': 'Individu'},
            'ancrage_approx': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "u'individus'", 'unique': 'True', 'null': 'True', 'to': u"orm['catalogue.AncrageSpatioTemporel']"}),
            'ancrage_deces': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "u'individus_decedes'", 'unique': 'True', 'null': 'True', 'to': u"orm['catalogue.AncrageSpatioTemporel']"}),
            'ancrage_naissance': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "u'individus_nes'", 'unique': 'True', 'null': 'True', 'to': u"orm['catalogue.AncrageSpatioTemporel']"}),
            'biographie': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'designation': ('django.db.models.fields.CharField', [], {'default': "u'S'", 'max_length': '1'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'enfants': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'parents'", 'symmetrical': 'False', 'through': u"orm['catalogue.ParenteDIndividus']", 'to': u"orm['catalogue.Individu']"}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'nom_naissance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'particule_nom': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'blank': 'True'}),
            'particule_nom_naissance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'blank': 'True'}),
            'prenoms': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'individus'", 'to': u"orm['catalogue.Prenom']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'professions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'individus'", 'to': u"orm['catalogue.Profession']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'pseudonyme': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'titre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '1', 'blank': 'True'})
        },
        u'catalogue.lieu': {
            'Meta': {'ordering': "[u'nom']", 'unique_together': "((u'nom', u'parent'),)", 'object_name': 'Lieu'},
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'blank': 'True'}),
            'historique': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nature': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'lieux'", 'to': u"orm['catalogue.NatureDeLieu']"}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfant'", 'null': 'True', 'to': u"orm['catalogue.Lieu']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'catalogue.naturedelieu': {
            'Meta': {'ordering': "[u'slug']", 'object_name': 'NatureDeLieu'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '430', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'referent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'get_slug'"})
        },
        u'catalogue.oeuvre': {
            'Meta': {'ordering': "[u'titre', u'genre', u'slug']", 'object_name': 'Oeuvre'},
            'ancrage_creation': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "u'oeuvres_creees'", 'unique': 'True', 'null': 'True', 'to': u"orm['catalogue.AncrageSpatioTemporel']"}),
            'caracteristiques': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.CaracteristiqueDOeuvre']", 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'contenu_dans': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfants'", 'null': 'True', 'to': u"orm['catalogue.Oeuvre']"}),
            'coordination': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'blank': 'True'}),
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'blank': 'True'}),
            'evenements': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'oeuvres'", 'symmetrical': 'False', 'through': u"orm['catalogue.ElementDeProgramme']", 'to': u"orm['catalogue.Evenement']"}),
            'filles': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'meres'", 'symmetrical': 'False', 'through': u"orm['catalogue.ParenteDOeuvres']", 'to': u"orm['catalogue.Oeuvre']"}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'oeuvres'", 'null': 'True', 'to': u"orm['catalogue.GenreDOeuvre']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lilypond': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'prefixe_titre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'blank': 'True'}),
            'prefixe_titre_secondaire': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'blank': 'True'}),
            'pupitres': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'oeuvres'", 'to': u"orm['catalogue.Pupitre']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'titre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'titre_secondaire': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'catalogue.parentedindividus': {
            'Meta': {'ordering': "(u'type', u'parent', u'enfant')", 'object_name': 'ParenteDIndividus'},
            'enfant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes'", 'to': u"orm['catalogue.Individu']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'enfances'", 'to': u"orm['catalogue.Individu']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes'", 'to': u"orm['catalogue.TypeDeParenteDIndividus']"})
        },
        u'catalogue.parentedoeuvres': {
            'Meta': {'ordering': "[u'type']", 'unique_together': "((u'type', u'mere', u'fille'),)", 'object_name': 'ParenteDOeuvres'},
            'fille': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes_meres'", 'to': u"orm['catalogue.Oeuvre']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mere': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes_filles'", 'to': u"orm['catalogue.Oeuvre']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes'", 'to': u"orm['catalogue.TypeDeParenteDOeuvres']"})
        },
        u'catalogue.partie': {
            'Meta': {'ordering': "[u'classement', u'nom']", 'object_name': 'Partie'},
            'classement': ('django.db.models.fields.FloatField', [], {'default': '1.0', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfant'", 'null': 'True', 'to': u"orm['catalogue.Partie']"}),
            'professions': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'parties'", 'symmetrical': 'False', 'to': u"orm['catalogue.Profession']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'get_slug'"}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'catalogue.personnel': {
            'Meta': {'object_name': 'Personnel'},
            'engagements': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'personnels'", 'symmetrical': 'False', 'to': u"orm['catalogue.Engagement']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'saison': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'personnels'", 'to': u"orm['catalogue.Saison']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'personnels'", 'to': u"orm['catalogue.TypeDePersonnel']"})
        },
        u'catalogue.prenom': {
            'Meta': {'ordering': "(u'classement', u'prenom')", 'object_name': 'Prenom'},
            'classement': ('django.db.models.fields.FloatField', [], {'default': '1.0', 'db_index': 'True'}),
            'favori': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'prenom': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        u'catalogue.profession': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'Profession'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_feminin': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfant'", 'null': 'True', 'to': u"orm['catalogue.Profession']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'catalogue.pupitre': {
            'Meta': {'ordering': "[u'partie']", 'object_name': 'Pupitre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'partie': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pupitres'", 'to': u"orm['catalogue.Partie']"}),
            'quantite_max': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'}),
            'quantite_min': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'})
        },
        u'catalogue.saison': {
            'Meta': {'ordering': "[u'lieu', u'debut']", 'object_name': 'Saison'},
            'debut': ('django.db.models.fields.DateField', [], {}),
            'fin': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lieu': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'saisons'", 'to': u"orm['catalogue.Lieu']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.source': {
            'Meta': {'ordering': "[u'date', u'nom', u'numero', u'page', u'type']", 'object_name': 'Source'},
            'contenu': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'blank': 'True'}),
            'evenements': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'sources'", 'to': u"orm['catalogue.Evenement']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'numero': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sources'", 'to': u"orm['catalogue.TypeDeSource']"})
        },
        u'catalogue.typedecaracteristiquedoeuvre': {
            'Meta': {'ordering': "[u'classement']", 'object_name': 'TypeDeCaracteristiqueDOeuvre'},
            'classement': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.typedeparentedindividus': {
            'Meta': {'ordering': "[u'classement']", 'object_name': 'TypeDeParenteDIndividus'},
            'classement': ('django.db.models.fields.FloatField', [], {'default': '1.0', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '55', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.typedeparentedoeuvres': {
            'Meta': {'ordering': "[u'classement']", 'object_name': 'TypeDeParenteDOeuvres'},
            'classement': ('django.db.models.fields.FloatField', [], {'default': '1.0', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'nom_relatif': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'nom_relatif_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '130', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.typedepersonnel': {
            'Meta': {'ordering': "[u'nom']", 'object_name': 'TypeDePersonnel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.typedesource': {
            'Meta': {'ordering': "[u'slug']", 'object_name': 'TypeDeSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'get_slug'"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['catalogue']