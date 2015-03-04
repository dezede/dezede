# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from libretto.migration_utils import was_applied


class Migration(SchemaMigration):

    def forwards(self, orm):

        if was_applied(__file__, 'catalogue'):
            return

        # Adding field 'Profession.classement'
        db.add_column(u'catalogue_profession', 'classement',
                      self.gf('django.db.models.fields.SmallIntegerField')(default=1, db_index=True),
                      keep_default=False)


        # Changing field 'CaracteristiqueDOeuvre.classement'
        db.alter_column(u'catalogue_caracteristiquedoeuvre', 'classement', self.gf('django.db.models.fields.SmallIntegerField')())

        # Changing field 'Prenom.classement'
        db.alter_column(u'catalogue_prenom', 'classement', self.gf('django.db.models.fields.SmallIntegerField')())

        # Changing field 'TypeDeParenteDOeuvres.classement'
        db.alter_column(u'catalogue_typedeparentedoeuvres', 'classement', self.gf('django.db.models.fields.SmallIntegerField')())

        # Changing field 'Partie.classement'
        db.alter_column(u'catalogue_partie', 'classement', self.gf('django.db.models.fields.SmallIntegerField')())

        # Changing field 'TypeDeCaracteristiqueDOeuvre.classement'
        db.alter_column(u'catalogue_typedecaracteristiquedoeuvre', 'classement', self.gf('django.db.models.fields.SmallIntegerField')())

        # Changing field 'CaracteristiqueDElementDeProgramme.classement'
        db.alter_column(u'catalogue_caracteristiquedelementdeprogramme', 'classement', self.gf('django.db.models.fields.SmallIntegerField')())

        # Changing field 'TypeDeParenteDIndividus.classement'
        db.alter_column(u'catalogue_typedeparentedindividus', 'classement', self.gf('django.db.models.fields.SmallIntegerField')())

    def backwards(self, orm):
        # Deleting field 'Profession.classement'
        db.delete_column(u'catalogue_profession', 'classement')


        # Changing field 'CaracteristiqueDOeuvre.classement'
        db.alter_column(u'catalogue_caracteristiquedoeuvre', 'classement', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'Prenom.classement'
        db.alter_column(u'catalogue_prenom', 'classement', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'TypeDeParenteDOeuvres.classement'
        db.alter_column(u'catalogue_typedeparentedoeuvres', 'classement', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'Partie.classement'
        db.alter_column(u'catalogue_partie', 'classement', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'TypeDeCaracteristiqueDOeuvre.classement'
        db.alter_column(u'catalogue_typedecaracteristiquedoeuvre', 'classement', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'CaracteristiqueDElementDeProgramme.classement'
        db.alter_column(u'catalogue_caracteristiquedelementdeprogramme', 'classement', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'TypeDeParenteDIndividus.classement'
        db.alter_column(u'catalogue_typedeparentedindividus', 'classement', self.gf('django.db.models.fields.FloatField')())

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'catalogue.ancragespatiotemporel': {
            'Meta': {'ordering': "(u'date', u'heure', u'lieu__parent', u'lieu', u'date_approx', u'heure_approx', u'lieu_approx')", 'object_name': 'AncrageSpatioTemporel'},
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'date_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'heure': ('django.db.models.fields.TimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'heure_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lieu': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'ancrages'", 'null': 'True', 'to': u"orm['catalogue.Lieu']"}),
            'lieu_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.auteur': {
            'Meta': {'ordering': "(u'profession', u'individu__nom')", 'object_name': 'Auteur'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individu': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'auteurs'", 'to': u"orm['catalogue.Individu']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'auteurs'", 'to': u"orm['catalogue.Profession']"})
        },
        u'catalogue.caracteristiquedelementdeprogramme': {
            'Meta': {'ordering': "(u'nom',)", 'object_name': 'CaracteristiqueDElementDeProgramme'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '110', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.caracteristiquedoeuvre': {
            'Meta': {'ordering': "(u'type', u'classement', u'valeur')", 'object_name': 'CaracteristiqueDOeuvre'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'caracteristiques_d_oeuvre'", 'to': u"orm['catalogue.TypeDeCaracteristiqueDOeuvre']"}),
            'valeur': ('django.db.models.fields.CharField', [], {'max_length': '400'})
        },
        u'catalogue.devise': {
            'Meta': {'object_name': 'Devise'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '200', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'symbole': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10', 'db_index': 'True'})
        },
        u'catalogue.document': {
            'Meta': {'ordering': "(u'document',)", 'object_name': 'Document'},
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'document': ('filebrowser.fields.FileBrowseField', [], {'max_length': '400'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.elementdedistribution': {
            'Meta': {'ordering': "(u'pupitre',)", 'object_name': 'ElementDeDistribution'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individus': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'elements_de_distribution'", 'symmetrical': 'False', 'to': u"orm['catalogue.Individu']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'numerotation': ('django.db.models.fields.CharField', [], {'default': "u'O'", 'max_length': '1'}),
            'oeuvre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'to': u"orm['catalogue.Oeuvre']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'personnels': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['catalogue.Personnel']"}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'catalogue.engagement': {
            'Meta': {'object_name': 'Engagement'},
            'devise': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'engagements'", 'null': 'True', 'to': u"orm['catalogue.Devise']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individus': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'engagements'", 'symmetrical': 'False', 'to': u"orm['catalogue.Individu']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'engagements'", 'to': u"orm['catalogue.Profession']"}),
            'salaire': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.etat': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'Etat'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'relache': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'})
        },
        u'catalogue.genredoeuvre': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'GenreDOeuvre'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '430', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'enfants'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['catalogue.GenreDOeuvre']"}),
            'referent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'get_slug'"})
        },
        u'catalogue.illustration': {
            'Meta': {'ordering': "(u'image',)", 'object_name': 'Illustration'},
            'commentaire': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('filebrowser.fields.FileBrowseField', [], {'max_length': '400'}),
            'legende': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'nom_naissance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'particule_nom': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'blank': 'True'}),
            'particule_nom_naissance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'blank': 'True'}),
            'prenoms': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'individus'", 'to': u"orm['catalogue.Prenom']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'professions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'individus'", 'to': u"orm['catalogue.Profession']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'pseudonyme': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'titre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '1', 'blank': 'True'})
        },
        u'catalogue.lieu': {
            'Meta': {'ordering': "(u'nom',)", 'unique_together': "((u'nom', u'parent'),)", 'object_name': 'Lieu'},
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'blank': 'True'}),
            'historique': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nature': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'lieux'", 'to': u"orm['catalogue.NatureDeLieu']"}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfants'", 'null': 'True', 'to': u"orm['catalogue.Lieu']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'catalogue.naturedelieu': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'NatureDeLieu'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '430', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'referent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'get_slug'"})
        },
        u'catalogue.oeuvre': {
            'Meta': {'ordering': "(u'titre', u'genre', u'slug')", 'object_name': 'Oeuvre'},
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lilypond': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'enfances'", 'to': u"orm['catalogue.Individu']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes'", 'to': u"orm['catalogue.TypeDeParenteDIndividus']"})
        },
        u'catalogue.parentedoeuvres': {
            'Meta': {'ordering': "(u'type',)", 'unique_together': "((u'type', u'mere', u'fille'),)", 'object_name': 'ParenteDOeuvres'},
            'fille': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes_meres'", 'to': u"orm['catalogue.Oeuvre']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mere': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes_filles'", 'to': u"orm['catalogue.Oeuvre']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes'", 'to': u"orm['catalogue.TypeDeParenteDOeuvres']"})
        },
        u'catalogue.partie': {
            'Meta': {'ordering': "(u'classement', u'nom')", 'object_name': 'Partie'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfant'", 'null': 'True', 'to': u"orm['catalogue.Partie']"}),
            'professions': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'parties'", 'symmetrical': 'False', 'to': u"orm['catalogue.Profession']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'catalogue.personnel': {
            'Meta': {'object_name': 'Personnel'},
            'engagements': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'personnels'", 'symmetrical': 'False', 'to': u"orm['catalogue.Engagement']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'saison': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'personnels'", 'to': u"orm['catalogue.Saison']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'personnels'", 'to': u"orm['catalogue.TypeDePersonnel']"})
        },
        u'catalogue.prenom': {
            'Meta': {'ordering': "(u'classement', u'prenom')", 'object_name': 'Prenom'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'favori': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'prenom': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        u'catalogue.profession': {
            'Meta': {'ordering': "(u'nom',)", 'object_name': 'Profession'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_feminin': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfant'", 'null': 'True', 'to': u"orm['catalogue.Profession']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'catalogue.pupitre': {
            'Meta': {'ordering': "(u'partie',)", 'object_name': 'Pupitre'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'partie': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pupitres'", 'to': u"orm['catalogue.Partie']"}),
            'quantite_max': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'}),
            'quantite_min': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'})
        },
        u'catalogue.saison': {
            'Meta': {'ordering': "(u'lieu', u'debut')", 'object_name': 'Saison'},
            'debut': ('django.db.models.fields.DateField', [], {}),
            'fin': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lieu': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'saisons'", 'to': u"orm['catalogue.Lieu']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.source': {
            'Meta': {'ordering': "(u'date', u'nom', u'numero', u'page', u'type')", 'object_name': 'Source'},
            'contenu': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'blank': 'True'}),
            'evenements': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'sources'", 'to': u"orm['catalogue.Evenement']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'numero': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sources'", 'to': u"orm['catalogue.TypeDeSource']"})
        },
        u'catalogue.typedecaracteristiquedoeuvre': {
            'Meta': {'ordering': "(u'classement',)", 'object_name': 'TypeDeCaracteristiqueDOeuvre'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.typedeparentedindividus': {
            'Meta': {'ordering': "(u'classement',)", 'object_name': 'TypeDeParenteDIndividus'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '55', 'blank': 'True'}),
            'nom_relatif': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'nom_relatif_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '55', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.typedeparentedoeuvres': {
            'Meta': {'ordering': "(u'classement',)", 'object_name': 'TypeDeParenteDOeuvres'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'nom_relatif': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'nom_relatif_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '130', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.typedepersonnel': {
            'Meta': {'ordering': "(u'nom',)", 'object_name': 'TypeDePersonnel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.typedesource': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'TypeDeSource'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'get_slug'"})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['catalogue']