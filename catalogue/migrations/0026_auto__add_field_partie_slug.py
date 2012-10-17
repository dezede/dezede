# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Partie.slug'
        db.add_column('catalogue_partie', 'slug',
                      self.gf('autoslug.fields.AutoSlugField')(default='', unique_with=(), max_length=50, populate_from=None),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Partie.slug'
        db.delete_column('catalogue_partie', 'slug')


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
        'catalogue.ancragespatiotemporel': {
            'Meta': {'ordering': "['date', 'heure', 'lieu__parent', 'lieu', 'date_approx', 'heure_approx', 'lieu_approx']", 'object_name': 'AncrageSpatioTemporel'},
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_approx': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'heure': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'heure_approx': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lieu': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ancrages'", 'null': 'True', 'to': "orm['catalogue.Lieu']"}),
            'lieu_approx': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'catalogue.attributiondepupitre': {
            'Meta': {'ordering': "['pupitre']", 'object_name': 'AttributionDePupitre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individus': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'attributions_de_pupitre'", 'symmetrical': 'False', 'to': "orm['catalogue.Individu']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'pupitre': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attributions_de_pupitre'", 'to': "orm['catalogue.Pupitre']"})
        },
        'catalogue.auteur': {
            'Meta': {'ordering': "['profession', 'individu__nom']", 'object_name': 'Auteur'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individu': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'auteurs'", 'to': "orm['catalogue.Individu']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'auteurs'", 'to': "orm['catalogue.Profession']"})
        },
        'catalogue.caracteristiquedelementdeprogramme': {
            'Meta': {'ordering': "['nom']", 'object_name': 'CaracteristiqueDElementDeProgramme'},
            'classement': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '110', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'catalogue.caracteristiquedoeuvre': {
            'Meta': {'ordering': "['type', 'classement']", 'object_name': 'CaracteristiqueDOeuvre'},
            'classement': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'caracteristiques_d_oeuvre'", 'to': "orm['catalogue.TypeDeCaracteristiqueDOeuvre']"}),
            'valeur': ('django.db.models.fields.CharField', [], {'max_length': '400'})
        },
        'catalogue.devise': {
            'Meta': {'object_name': 'Devise'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'symbole': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'})
        },
        'catalogue.document': {
            'Meta': {'ordering': "['document']", 'object_name': 'Document'},
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'document': ('filebrowser.fields.FileBrowseField', [], {'max_length': '400'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'catalogue.elementdeprogramme': {
            'Meta': {'ordering': "['position', 'oeuvre']", 'object_name': 'ElementDeProgramme'},
            'autre': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'caracteristiques': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'elements_de_programme'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['catalogue.CaracteristiqueDElementDeProgramme']"}),
            'distribution': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'elements_de_programme'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['catalogue.AttributionDePupitre']"}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalogue.Etat']", 'null': 'True', 'blank': 'True'}),
            'evenement': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'programme'", 'to': "orm['catalogue.Evenement']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'oeuvre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'elements_de_programme'", 'null': 'True', 'to': "orm['catalogue.Oeuvre']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'personnels': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'elements_de_programme'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['catalogue.Personnel']"}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        'catalogue.engagement': {
            'Meta': {'object_name': 'Engagement'},
            'devise': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'engagements'", 'null': 'True', 'to': "orm['catalogue.Devise']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individus': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'engagements'", 'symmetrical': 'False', 'to': "orm['catalogue.Individu']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'engagements'", 'to': "orm['catalogue.Profession']"}),
            'salaire': ('django.db.models.fields.FloatField', [], {'blank': 'True'})
        },
        'catalogue.etat': {
            'Meta': {'ordering': "['slug']", 'object_name': 'Etat'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None'})
        },
        'catalogue.evenement': {
            'Meta': {'ordering': "['ancrage_debut']", 'object_name': 'Evenement'},
            'ancrage_debut': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'evenements_debuts'", 'unique': 'True', 'to': "orm['catalogue.AncrageSpatioTemporel']"}),
            'ancrage_fin': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'evenements_fins'", 'unique': 'True', 'null': 'True', 'to': "orm['catalogue.AncrageSpatioTemporel']"}),
            'circonstance': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalogue.Etat']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'relache': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'catalogue.genredoeuvre': {
            'Meta': {'ordering': "['slug']", 'object_name': 'GenreDOeuvre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '430', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'enfants'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['catalogue.GenreDOeuvre']"}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None'})
        },
        'catalogue.illustration': {
            'Meta': {'ordering': "['image']", 'object_name': 'Illustration'},
            'commentaire': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('filebrowser.fields.FileBrowseField', [], {'max_length': '400'}),
            'legende': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'catalogue.individu': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Individu'},
            'ancrage_approx': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'individus'", 'unique': 'True', 'null': 'True', 'to': "orm['catalogue.AncrageSpatioTemporel']"}),
            'ancrage_deces': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'individus_decedes'", 'unique': 'True', 'null': 'True', 'to': "orm['catalogue.AncrageSpatioTemporel']"}),
            'ancrage_naissance': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'individus_nes'", 'unique': 'True', 'null': 'True', 'to': "orm['catalogue.AncrageSpatioTemporel']"}),
            'biographie': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'designation': ('django.db.models.fields.CharField', [], {'default': "'S'", 'max_length': '1'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalogue.Etat']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'nom_naissance': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parentes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'individus_orig'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['catalogue.ParenteDIndividus']"}),
            'particule_nom': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'particule_nom_naissance': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'prenoms': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'individus'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['catalogue.Prenom']"}),
            'professions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'individus'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['catalogue.Profession']"}),
            'pseudonyme': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': 'None', 'unique_with': '()'}),
            'titre': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'})
        },
        'catalogue.lieu': {
            'Meta': {'ordering': "['nom']", 'unique_together': "(('nom', 'parent'),)", 'object_name': 'Lieu'},
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalogue.Etat']", 'null': 'True', 'blank': 'True'}),
            'historique': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nature': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lieux'", 'to': "orm['catalogue.NatureDeLieu']"}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'enfant'", 'null': 'True', 'to': "orm['catalogue.Lieu']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': 'None', 'unique_with': '()'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'catalogue.naturedelieu': {
            'Meta': {'ordering': "['slug']", 'object_name': 'NatureDeLieu'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '430', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'referent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None'})
        },
        'catalogue.oeuvre': {
            'Meta': {'ordering': "['genre', 'slug']", 'object_name': 'Oeuvre'},
            'ancrage_creation': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'oeuvres_creees'", 'unique': 'True', 'null': 'True', 'to': "orm['catalogue.AncrageSpatioTemporel']"}),
            'caracteristiques': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['catalogue.CaracteristiqueDOeuvre']", 'null': 'True', 'blank': 'True'}),
            'coordination': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalogue.Etat']", 'null': 'True', 'blank': 'True'}),
            'evenements': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'oeuvres'", 'symmetrical': 'False', 'through': "orm['catalogue.ElementDeProgramme']", 'to': "orm['catalogue.Evenement']"}),
            'filles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'meres'", 'symmetrical': 'False', 'through': "orm['catalogue.ParenteDOeuvres']", 'to': "orm['catalogue.Oeuvre']"}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'oeuvres'", 'null': 'True', 'to': "orm['catalogue.GenreDOeuvre']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'lilypond': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'prefixe_titre': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'prefixe_titre_secondaire': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'pupitres': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'oeuvres'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['catalogue.Pupitre']"}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': 'None', 'unique_with': '()'}),
            'titre': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'titre_secondaire': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'catalogue.parentedindividus': {
            'Meta': {'ordering': "['type']", 'object_name': 'ParenteDIndividus'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individus_cibles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'enfances_cibles'", 'symmetrical': 'False', 'to': "orm['catalogue.Individu']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parentes'", 'to': "orm['catalogue.TypeDeParenteDIndividus']"})
        },
        'catalogue.parentedoeuvres': {
            'Meta': {'ordering': "['type']", 'unique_together': "(('type', 'mere', 'fille'),)", 'object_name': 'ParenteDOeuvres'},
            'fille': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parentes_meres'", 'to': "orm['catalogue.Oeuvre']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mere': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parentes_filles'", 'to': "orm['catalogue.Oeuvre']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parentes'", 'to': "orm['catalogue.TypeDeParenteDOeuvres']"})
        },
        'catalogue.partie': {
            'Meta': {'ordering': "['classement', 'nom']", 'object_name': 'Partie'},
            'classement': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parente': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'enfant'", 'null': 'True', 'to': "orm['catalogue.Partie']"}),
            'professions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'parties'", 'symmetrical': 'False', 'to': "orm['catalogue.Profession']"}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None'})
        },
        'catalogue.personnel': {
            'Meta': {'object_name': 'Personnel'},
            'engagements': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'personnels'", 'symmetrical': 'False', 'to': "orm['catalogue.Engagement']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'saison': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'personnels'", 'to': "orm['catalogue.Saison']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'personnels'", 'to': "orm['catalogue.TypeDePersonnel']"})
        },
        'catalogue.prenom': {
            'Meta': {'ordering': "['prenom', 'classement']", 'object_name': 'Prenom'},
            'classement': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'favori': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'prenom': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'catalogue.profession': {
            'Meta': {'ordering': "['slug']", 'object_name': 'Profession'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'nom_feminin': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parente': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'enfant'", 'null': 'True', 'to': "orm['catalogue.Profession']"}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None'})
        },
        'catalogue.pupitre': {
            'Meta': {'ordering': "['partie']", 'object_name': 'Pupitre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'partie': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pupitres'", 'to': "orm['catalogue.Partie']"}),
            'quantite_max': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'quantite_min': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'catalogue.saison': {
            'Meta': {'ordering': "['lieu', 'debut']", 'object_name': 'Saison'},
            'debut': ('django.db.models.fields.DateField', [], {}),
            'fin': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lieu': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'saisons'", 'to': "orm['catalogue.Lieu']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'catalogue.source': {
            'Meta': {'ordering': "['date', 'nom', 'numero', 'page', 'type']", 'object_name': 'Source'},
            'contenu': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalogue.Etat']", 'null': 'True', 'blank': 'True'}),
            'evenements': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'sources'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['catalogue.Evenement']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'numero': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sources'", 'to': "orm['catalogue.TypeDeSource']"})
        },
        'catalogue.typedecaracteristiquedoeuvre': {
            'Meta': {'ordering': "['classement']", 'object_name': 'TypeDeCaracteristiqueDOeuvre'},
            'classement': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'catalogue.typedeparentedindividus': {
            'Meta': {'ordering': "['classement']", 'object_name': 'TypeDeParenteDIndividus'},
            'classement': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '55', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'catalogue.typedeparentedoeuvres': {
            'Meta': {'ordering': "['classement']", 'object_name': 'TypeDeParenteDOeuvres'},
            'classement': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'nom_relatif': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'nom_relatif_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '130', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'catalogue.typedepersonnel': {
            'Meta': {'ordering': "['nom']", 'object_name': 'TypeDePersonnel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'catalogue.typedesource': {
            'Meta': {'ordering': "['slug']", 'object_name': 'TypeDeSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None'})
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