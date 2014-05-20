# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CategorieDeDossiers'
        db.create_table(u'dossiers_categoriededossiers', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'categoriededossiers', null=True, on_delete=models.PROTECT, to=orm['accounts.HierarchicUser'])),
            ('etat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['libretto.Etat'], on_delete=models.PROTECT)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('position', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
        ))
        db.send_create_signal(u'dossiers', ['CategorieDeDossiers'])

        # Adding field 'DossierDEvenements.categorie'
        db.add_column(u'dossiers_dossierdevenements', 'categorie',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'dossiersdevenements', null=True, to=orm['dossiers.CategorieDeDossiers']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'CategorieDeDossiers'
        db.delete_table(u'dossiers_categoriededossiers')

        # Deleting field 'DossierDEvenements.categorie'
        db.delete_column(u'dossiers_dossierdevenements', 'categorie_id')


    models = {
        u'accounts.hierarchicuser': {
            'Meta': {'ordering': "(u'last_name', u'first_name')", 'object_name': 'HierarchicUser'},
            'avatar': ('filebrowser.fields.FileBrowseField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'fonctions': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '75', 'blank': 'True'}),
            'legal_person': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'literature': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'mentor': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'disciples'", 'null': 'True', 'to': u"orm['accounts.HierarchicUser']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'presentation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'show_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'website_verbose': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'willing_to_be_mentor': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'dossiers.categoriededossiers': {
            'Meta': {'ordering': "(u'position',)", 'object_name': 'CategorieDeDossiers'},
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'categoriededossiers'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'})
        },
        u'dossiers.dossierdevenements': {
            'Meta': {'ordering': "(u'tree_id', u'lft')", 'object_name': 'DossierDEvenements'},
            'auteurs': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'dossiers'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Individu']"}),
            'bibliographie': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'categorie': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'dossiersdevenements'", 'null': 'True', 'to': u"orm['dossiers.CategorieDeDossiers']"}),
            'circonstance': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'contexte': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_publication': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'debut': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'developpements': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'editeurs_scientifiques': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'dossiers_d_evenements_edites'", 'symmetrical': 'False', 'to': u"orm['accounts.HierarchicUser']"}),
            'ensembles': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'dossiers'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Ensemble']"}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            'evenements': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'dossiers'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Evenement']"}),
            'fin': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lieux': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'dossiers'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Lieu']"}),
            'oeuvres': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'dossiers'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Oeuvre']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'dossierdevenements'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'children'", 'null': 'True', 'to': u"orm['dossiers.DossierDEvenements']"}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'presentation': ('django.db.models.fields.TextField', [], {}),
            'publications': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'sources': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'titre': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'titre_court': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'libretto.ancragespatiotemporel': {
            'Meta': {'ordering': "(u'date', u'heure', u'lieu', u'date_approx', u'heure_approx', u'lieu_approx')", 'object_name': 'AncrageSpatioTemporel'},
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'date_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'heure': ('django.db.models.fields.TimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'heure_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lieu': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'ancrages'", 'null': 'True', 'to': u"orm['libretto.Lieu']"}),
            'lieu_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'ancragespatiotemporel'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"})
        },
        u'libretto.auteur': {
            'Meta': {'ordering': "(u'profession', u'individu__nom')", 'object_name': 'Auteur'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individu': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'auteurs'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Individu']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'auteur'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'auteurs'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Profession']"})
        },
        u'libretto.caracteristique': {
            'Meta': {'ordering': "(u'type', u'classement', u'valeur')", 'object_name': 'Caracteristique'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'caracteristique'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_libretto.caracteristique_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'caracteristiques'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.TypeDeCaracteristique']"}),
            'valeur': ('django.db.models.fields.CharField', [], {'max_length': '400'})
        },
        u'libretto.caracteristiquedensemble': {
            'Meta': {'ordering': "(u'type', u'classement', u'valeur')", 'object_name': 'CaracteristiqueDEnsemble', '_ormbases': [u'libretto.Caracteristique']},
            u'caracteristique_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['libretto.Caracteristique']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'libretto.caracteristiquedeprogramme': {
            'Meta': {'ordering': "(u'type', u'classement', u'valeur')", 'object_name': 'CaracteristiqueDeProgramme', '_ormbases': [u'libretto.Caracteristique']},
            u'caracteristique_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['libretto.Caracteristique']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'libretto.caracteristiquedoeuvre': {
            'Meta': {'ordering': "(u'type', u'classement', u'valeur')", 'object_name': 'CaracteristiqueDOeuvre', '_ormbases': [u'libretto.Caracteristique']},
            u'caracteristique_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['libretto.Caracteristique']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'libretto.document': {
            'Meta': {'ordering': "(u'document',)", 'object_name': 'Document'},
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'document': ('filebrowser.fields.FileBrowseField', [], {'max_length': '400'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'document'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"})
        },
        u'libretto.elementdedistribution': {
            'Meta': {'ordering': "(u'pupitre', u'profession')", 'object_name': 'ElementDeDistribution'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'ensembles': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'elements_de_distribution'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Ensemble']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individus': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'elements_de_distribution'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Individu']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elementdedistribution'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_distribution'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Profession']"}),
            'pupitre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_distribution'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Pupitre']"})
        },
        u'libretto.ensemble': {
            'Meta': {'object_name': 'Ensemble'},
            'caracteristiques': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'ensembles'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.CaracteristiqueDEnsemble']"}),
            'debut': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'debut_precision': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'ensemble_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Document']"}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            'fin': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'fin_precision': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'ensemble_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Illustration']"}),
            'individus': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'ensembles'", 'symmetrical': 'False', 'through': u"orm['libretto.Membre']", 'to': u"orm['libretto.Individu']"}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '75', 'db_index': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'ensemble'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'particule_nom': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '5', 'blank': 'True'}),
            'siege': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'ensembles'", 'null': 'True', 'to': u"orm['libretto.Lieu']"}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'})
        },
        u'libretto.etat': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'Etat'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'etat'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'})
        },
        u'libretto.evenement': {
            'Meta': {'ordering': "(u'ancrage_debut',)", 'object_name': 'Evenement'},
            'ancrage_debut': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'evenements_debuts'", 'unique': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.AncrageSpatioTemporel']"}),
            'ancrage_fin': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'evenements_fins'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.AncrageSpatioTemporel']", 'blank': 'True', 'unique': 'True'}),
            'caracteristiques': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'evenements'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.CaracteristiqueDeProgramme']"}),
            'circonstance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '500', 'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'evenement_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Document']"}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'evenement_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Illustration']"}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'evenement'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'relache': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'})
        },
        u'libretto.genredoeuvre': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'GenreDOeuvre'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '430', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'genredoeuvre'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'parents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'enfants'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.GenreDOeuvre']"}),
            'referent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'get_slug'"})
        },
        u'libretto.illustration': {
            'Meta': {'ordering': "(u'image',)", 'object_name': 'Illustration'},
            'commentaire': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('filebrowser.fields.FileBrowseField', [], {'max_length': '400'}),
            'legende': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'illustration'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"})
        },
        u'libretto.individu': {
            'Meta': {'ordering': "(u'nom',)", 'object_name': 'Individu'},
            'ancrage_approx': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'individus'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.AncrageSpatioTemporel']", 'blank': 'True', 'unique': 'True'}),
            'ancrage_deces': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'individus_decedes'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.AncrageSpatioTemporel']", 'blank': 'True', 'unique': 'True'}),
            'ancrage_naissance': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'individus_nes'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.AncrageSpatioTemporel']", 'blank': 'True', 'unique': 'True'}),
            'biographie': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'designation': ('django.db.models.fields.CharField', [], {'default': "u'S'", 'max_length': '1'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'individu_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Document']"}),
            'enfants': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'parents'", 'symmetrical': 'False', 'through': u"orm['libretto.ParenteDIndividus']", 'to': u"orm['libretto.Individu']"}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'individu_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Illustration']"}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'nom_naissance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'individu'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'particule_nom': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'blank': 'True'}),
            'particule_nom_naissance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'blank': 'True'}),
            'prenoms': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'individus'", 'to': u"orm['libretto.Prenom']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'professions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'individus'", 'to': u"orm['libretto.Profession']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'pseudonyme': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'titre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '1', 'blank': 'True'})
        },
        u'libretto.instrument': {
            'Meta': {'ordering': "(u'classement', u'nom')", 'object_name': 'Instrument', '_ormbases': [u'libretto.Partie']},
            u'partie_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['libretto.Partie']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'libretto.lieu': {
            'Meta': {'ordering': "(u'nom',)", 'unique_together': "((u'nom', u'parent'),)", 'object_name': 'Lieu'},
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'lieu_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Document']"}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            'historique': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'lieu_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Illustration']"}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nature': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'lieux'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.NatureDeLieu']"}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'lieu'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'parent': ('polymorphic_tree.models.PolymorphicTreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfants'", 'null': 'True', 'to': u"orm['libretto.Lieu']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_libretto.lieu_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'libretto.membre': {
            'Meta': {'ordering': "(u'instrument', u'classement')", 'object_name': 'Membre'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'debut': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'debut_precision': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'ensemble': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'membres'", 'to': u"orm['libretto.Ensemble']"}),
            'fin': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'fin_precision': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individu': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'membres'", 'to': u"orm['libretto.Individu']"}),
            'instrument': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'membres'", 'null': 'True', 'to': u"orm['libretto.Instrument']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'membre'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"})
        },
        u'libretto.naturedelieu': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'NatureDeLieu'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '430', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'naturedelieu'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'referent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'get_slug'"})
        },
        u'libretto.oeuvre': {
            'Meta': {'ordering': "(u'titre', u'genre', u'slug')", 'object_name': 'Oeuvre'},
            'ancrage_creation': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'oeuvres_creees'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.AncrageSpatioTemporel']", 'blank': 'True', 'unique': 'True'}),
            'caracteristiques': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'oeuvres'", 'to': u"orm['libretto.CaracteristiqueDOeuvre']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'contenu_dans': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfants'", 'null': 'True', 'to': u"orm['libretto.Oeuvre']"}),
            'coordination': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'blank': 'True'}),
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'oeuvre_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Document']"}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            'filles': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'meres'", 'symmetrical': 'False', 'through': u"orm['libretto.ParenteDOeuvres']", 'to': u"orm['libretto.Oeuvre']"}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'oeuvres'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.GenreDOeuvre']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'oeuvre_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Illustration']"}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lilypond': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'oeuvre'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'prefixe_titre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'blank': 'True'}),
            'prefixe_titre_secondaire': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'blank': 'True'}),
            'pupitres': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'oeuvres'", 'to': u"orm['libretto.Pupitre']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'titre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'titre_secondaire': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'libretto.parentedindividus': {
            'Meta': {'ordering': "(u'type', u'parent', u'enfant')", 'object_name': 'ParenteDIndividus'},
            'enfant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Individu']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'parentedindividus'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'enfances'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Individu']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.TypeDeParenteDIndividus']"})
        },
        u'libretto.parentedoeuvres': {
            'Meta': {'ordering': "(u'type',)", 'unique_together': "((u'type', u'mere', u'fille'),)", 'object_name': 'ParenteDOeuvres'},
            'fille': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes_meres'", 'to': u"orm['libretto.Oeuvre']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mere': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes_filles'", 'to': u"orm['libretto.Oeuvre']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'parentedoeuvres'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.TypeDeParenteDOeuvres']"})
        },
        u'libretto.partie': {
            'Meta': {'ordering': "(u'classement', u'nom')", 'object_name': 'Partie'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'partie_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Document']"}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'partie_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Illustration']"}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'partie'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'parent': ('polymorphic_tree.models.PolymorphicTreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfant'", 'null': 'True', 'to': u"orm['libretto.Partie']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_libretto.partie_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'professions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'parties'", 'to': u"orm['libretto.Profession']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'libretto.prenom': {
            'Meta': {'ordering': "(u'classement', u'prenom')", 'object_name': 'Prenom'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'favori': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'prenom'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'prenom': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        u'libretto.profession': {
            'Meta': {'ordering': "(u'classement', u'nom')", 'object_name': 'Profession'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'profession_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Document']"}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'profession_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Illustration']"}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_feminin': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'profession'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfants'", 'null': 'True', 'to': u"orm['libretto.Profession']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'libretto.pupitre': {
            'Meta': {'ordering': "(u'partie',)", 'object_name': 'Pupitre'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'pupitre'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'partie': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pupitres'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Partie']"}),
            'quantite_max': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'}),
            'quantite_min': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'})
        },
        u'libretto.typedecaracteristique': {
            'Meta': {'ordering': "(u'classement',)", 'object_name': 'TypeDeCaracteristique'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'typedecaracteristique'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_libretto.typedecaracteristique_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"})
        },
        u'libretto.typedeparente': {
            'Meta': {'ordering': "(u'classement',)", 'unique_together': "((u'nom', u'nom_relatif'),)", 'object_name': 'TypeDeParente'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '55', 'blank': 'True'}),
            'nom_relatif': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'nom_relatif_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '130', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'typedeparente'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_libretto.typedeparente_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"})
        },
        u'libretto.typedeparentedindividus': {
            'Meta': {'ordering': "(u'classement',)", 'object_name': 'TypeDeParenteDIndividus', '_ormbases': [u'libretto.TypeDeParente']},
            u'typedeparente_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['libretto.TypeDeParente']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'libretto.typedeparentedoeuvres': {
            'Meta': {'ordering': "(u'classement',)", 'object_name': 'TypeDeParenteDOeuvres', '_ormbases': [u'libretto.TypeDeParente']},
            u'typedeparente_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['libretto.TypeDeParente']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['dossiers']