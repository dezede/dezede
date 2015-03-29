# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        ElementDeDistribution = orm['libretto.ElementDeDistribution']
        Pupitre = orm['libretto.Pupitre']

        # Checks if all Pupitre use nothing but a single Partie.
        assert not Pupitre.objects.filter(
            pk__in=ElementDeDistribution.objects.values('pupitre'),
            quantite_min__gt=1,
            quantite_max__gt=1,
        ).exists()

        for el in ElementDeDistribution.objects.exclude(
                pupitre=None).select_related('pupitre'):
            el.partie_id = el.pupitre.partie_id
            el.save()

    def backwards(self, orm):
        raise NotImplementedError

    models = {
        u'accounts.hierarchicuser': {
            'Meta': {'ordering': "(u'last_name', u'first_name')", 'object_name': 'HierarchicUser'},
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'fonctions': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
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
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
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
        u'libretto.auteur': {
            'Meta': {'ordering': "(u'profession', u'individu__nom')", 'object_name': 'Auteur'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individu': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'auteurs'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Individu']"}),
            'oeuvre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'auteurs'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Oeuvre']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'auteur'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'auteurs'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Profession']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'auteurs'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Source']"})
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
        u'libretto.devise': {
            'Meta': {'object_name': 'Devise'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '200', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'devise'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'symbole': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10', 'db_index': 'True'})
        },
        u'libretto.elementdedistribution': {
            'Meta': {'ordering': "(u'partie', u'profession', u'individu', u'ensemble')", 'object_name': 'ElementDeDistribution'},
            'ensemble': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_distribution'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Ensemble']"}),
            'evenement': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'distribution'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Evenement']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individu': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_distribution'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Individu']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elementdedistribution'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'partie': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_distribution'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Partie']"}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_distribution'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Profession']"}),
            'pupitre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_distribution'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Pupitre']"})
        },
        u'libretto.elementdeprogramme': {
            'Meta': {'ordering': "(u'position', u'oeuvre')", 'object_name': 'ElementDeProgramme'},
            'autre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '500', 'blank': 'True'}),
            'caracteristiques': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.CaracteristiqueDeProgramme']"}),
            'distribution': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.ElementDeDistribution']"}),
            'evenement': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'programme'", 'to': u"orm['libretto.Evenement']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'numerotation': ('django.db.models.fields.CharField', [], {'default': "u'O'", 'max_length': '1'}),
            'oeuvre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Oeuvre']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elementdeprogramme'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'part_d_auteur': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'personnels': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Personnel']"}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True'})
        },
        u'libretto.engagement': {
            'Meta': {'object_name': 'Engagement'},
            'devise': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'engagements'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Devise']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individus': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'engagements'", 'symmetrical': 'False', 'to': u"orm['libretto.Individu']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'engagement'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'engagements'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Profession']"}),
            'salaire': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'libretto.ensemble': {
            'Meta': {'object_name': 'Ensemble'},
            'caracteristiques': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'ensembles'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.CaracteristiqueDEnsemble']"}),
            'debut': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'debut_precision': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'default': '10', 'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            'fin': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'fin_precision': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individus': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'ensembles'", 'symmetrical': 'False', 'through': u"orm['libretto.Membre']", 'to': u"orm['libretto.Individu']"}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '75', 'db_index': 'True'}),
            'notes_privees': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'notes_publiques': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
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
            'Meta': {'ordering': "(u'debut_date', u'debut_heure', u'debut_lieu', u'debut_date_approx', u'debut_heure_approx', u'debut_lieu_approx')", 'object_name': 'Evenement'},
            'caracteristiques': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'evenements'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.CaracteristiqueDeProgramme']"}),
            'circonstance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '500', 'blank': 'True'}),
            'code_programme': ('django.db.models.fields.CharField', [], {'max_length': '55', 'blank': 'True'}),
            u'debut_date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            u'debut_date_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            u'debut_heure': ('django.db.models.fields.TimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'debut_heure_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            u'debut_lieu': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'evenement_debut_set'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Lieu']"}),
            u'debut_lieu_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'default': '10', 'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            'exoneres': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'fin_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'fin_date_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            u'fin_heure': ('django.db.models.fields.TimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'fin_heure_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            u'fin_lieu': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'evenement_fin_set'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Lieu']"}),
            u'fin_lieu_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'frequentation': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jauge': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'notes_privees': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'notes_publiques': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'evenement'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'payantes': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'programme_incomplet': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'recette_generale': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'recette_par_billets': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'relache': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'scolaires': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'libretto.fichier': {
            'Meta': {'ordering': "(u'source', u'position')", 'object_name': 'Fichier'},
            'duration': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'extract': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'extract_from'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['libretto.Fichier']", 'blank': 'True', 'unique': 'True'}),
            'fichier': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'folio': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'format': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'height': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'fichier'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'fichiers'", 'to': u"orm['libretto.Source']"}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
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
        u'libretto.individu': {
            'Meta': {'ordering': "(u'nom',)", 'object_name': 'Individu'},
            'biographie': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            u'deces_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'deces_date_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            u'deces_lieu': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'individu_deces_set'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Lieu']"}),
            u'deces_lieu_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'designation': ('django.db.models.fields.CharField', [], {'default': "u'S'", 'max_length': '1'}),
            'enfants': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'parents'", 'symmetrical': 'False', 'through': u"orm['libretto.ParenteDIndividus']", 'to': u"orm['libretto.Individu']"}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'default': '10', 'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isni': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            u'naissance_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'naissance_date_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            u'naissance_lieu': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'individu_naissance_set'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Lieu']"}),
            u'naissance_lieu_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'nom_naissance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'notes_privees': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'notes_publiques': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'individu'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'particule_nom': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'blank': 'True'}),
            'particule_nom_naissance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'blank': 'True'}),
            'prenoms': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'prenoms_complets': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'blank': 'True'}),
            'professions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'individus'", 'to': u"orm['libretto.Profession']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'pseudonyme': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'titre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '1', 'blank': 'True'})
        },
        u'libretto.institution': {
            'Meta': {'ordering': "(u'nom',)", 'object_name': 'Institution', '_ormbases': [u'libretto.Lieu']},
            u'lieu_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['libretto.Lieu']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'libretto.instrument': {
            'Meta': {'ordering': "(u'classement', u'nom')", 'object_name': 'Instrument', '_ormbases': [u'libretto.Partie']},
            u'partie_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['libretto.Partie']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'libretto.lieu': {
            'Meta': {'ordering': "(u'nom',)", 'unique_together': "((u'nom', u'parent'),)", 'object_name': 'Lieu', 'index_together': "((u'tree_id', u'level', u'lft', u'rght'),)"},
            'code_postal': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'default': '10', 'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            'geometry': ('django.contrib.gis.db.models.fields.GeometryField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'historique': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nature': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'lieux'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.NatureDeLieu']"}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'notes_privees': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'notes_publiques': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'lieu'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'parent': ('polymorphic_tree.models.PolymorphicTreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfants'", 'null': 'True', 'to': u"orm['libretto.Lieu']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_libretto.lieu_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'type_de_scene': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'})
        },
        u'libretto.lieudivers': {
            'Meta': {'ordering': "(u'nom',)", 'object_name': 'LieuDivers', '_ormbases': [u'libretto.Lieu']},
            u'lieu_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['libretto.Lieu']", 'unique': 'True', 'primary_key': 'True'})
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
            'Meta': {'ordering': "(u'type_extrait', u'numero_extrait', u'titre', u'genre', u'numero', u'coupe', u'tempo', u'tonalite', u'surnom', u'nom_courant', u'incipit', u'opus', u'ict')", 'object_name': 'Oeuvre'},
            'caracteristiques': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'oeuvres'", 'to': u"orm['libretto.CaracteristiqueDOeuvre']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'coordination': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'blank': 'True'}),
            'coupe': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'creation_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'creation_date_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            u'creation_heure': ('django.db.models.fields.TimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'creation_heure_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            u'creation_lieu': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'oeuvre_creation_set'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Lieu']"}),
            u'creation_lieu_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'default': '10', 'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            'extrait_de': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfants'", 'null': 'True', 'to': u"orm['libretto.Oeuvre']"}),
            'filles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'meres'", 'to': u"orm['libretto.Oeuvre']", 'through': u"orm['libretto.ParenteDOeuvres']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'oeuvres'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.GenreDOeuvre']"}),
            'ict': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incipit': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nom_courant': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'}),
            'notes_privees': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'notes_publiques': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'numero': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'numero_extrait': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'opus': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'oeuvre'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'prefixe_titre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'blank': 'True'}),
            'prefixe_titre_secondaire': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'blank': 'True'}),
            'pupitres': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'oeuvres'", 'to': u"orm['libretto.Pupitre']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'sujet': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'surnom': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'tempo': ('django.db.models.fields.CharField', [], {'max_length': '92', 'blank': 'True'}),
            'titre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'titre_secondaire': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'tonalite': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'type_extrait': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
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
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'default': '10', 'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'notes_privees': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'notes_publiques': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'partie'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'parent': ('polymorphic_tree.models.PolymorphicTreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfant'", 'null': 'True', 'to': u"orm['libretto.Partie']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_libretto.partie_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'professions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'parties'", 'to': u"orm['libretto.Profession']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'libretto.personnel': {
            'Meta': {'object_name': 'Personnel'},
            'engagements': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'personnels'", 'symmetrical': 'False', 'to': u"orm['libretto.Engagement']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'personnel'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'saison': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'personnels'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Saison']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'personnels'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.TypeDePersonnel']"})
        },
        u'libretto.profession': {
            'Meta': {'ordering': "(u'classement', u'nom')", 'object_name': 'Profession'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'default': '10', 'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_feminin': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'notes_privees': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'notes_publiques': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
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
        u'libretto.role': {
            'Meta': {'ordering': "(u'classement', u'nom')", 'object_name': 'Role', '_ormbases': [u'libretto.Partie']},
            'oeuvre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'roles'", 'null': 'True', 'to': u"orm['libretto.Oeuvre']"}),
            u'partie_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['libretto.Partie']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'libretto.saison': {
            'Meta': {'ordering': "(u'lieu', u'debut')", 'object_name': 'Saison'},
            'debut': ('django.db.models.fields.DateField', [], {}),
            'ensemble': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'saisons'", 'null': 'True', 'to': u"orm['libretto.Ensemble']"}),
            'fin': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lieu': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'saisons'", 'null': 'True', 'to': u"orm['libretto.Lieu']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'saison'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"})
        },
        u'libretto.source': {
            'Meta': {'ordering': "(u'date', u'titre', u'numero', u'page', u'lieu_conservation', u'cote')", 'object_name': 'Source'},
            'cote': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '35', 'blank': 'True'}),
            u'date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'date_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'ensembles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'sources'", 'symmetrical': 'False', 'through': u"orm['libretto.SourceEnsemble']", 'to': u"orm['libretto.Ensemble']"}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'default': '10', 'to': u"orm['libretto.Etat']", 'on_delete': 'models.PROTECT'}),
            'evenements': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'sources'", 'symmetrical': 'False', 'through': u"orm['libretto.SourceEvenement']", 'to': u"orm['libretto.Evenement']"}),
            'folio': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individus': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'sources'", 'symmetrical': 'False', 'through': u"orm['libretto.SourceIndividu']", 'to': u"orm['libretto.Individu']"}),
            'legende': ('django.db.models.fields.CharField', [], {'max_length': '600', 'blank': 'True'}),
            'lieu_conservation': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'lieux': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'sources'", 'symmetrical': 'False', 'through': u"orm['libretto.SourceLieu']", 'to': u"orm['libretto.Lieu']"}),
            'notes_privees': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'notes_publiques': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'numero': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'oeuvres': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'sources'", 'symmetrical': 'False', 'through': u"orm['libretto.SourceOeuvre']", 'to': u"orm['libretto.Oeuvre']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'source'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'page': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'blank': 'True'}),
            'parties': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'sources'", 'symmetrical': 'False', 'through': u"orm['libretto.SourcePartie']", 'to': u"orm['libretto.Partie']"}),
            'titre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'transcription': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sources'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.TypeDeSource']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'libretto.sourceensemble': {
            'Meta': {'unique_together': "((u'source', u'ensemble'),)", 'object_name': 'SourceEnsemble', 'db_table': "u'libretto_source_ensembles'"},
            'ensemble': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sourceensemble_set'", 'to': u"orm['libretto.Ensemble']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sourceensemble_set'", 'to': u"orm['libretto.Source']"})
        },
        u'libretto.sourceevenement': {
            'Meta': {'unique_together': "((u'source', u'evenement'),)", 'object_name': 'SourceEvenement', 'db_table': "u'libretto_source_evenements'"},
            'evenement': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sourceevenement_set'", 'to': u"orm['libretto.Evenement']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sourceevenement_set'", 'to': u"orm['libretto.Source']"})
        },
        u'libretto.sourceindividu': {
            'Meta': {'unique_together': "((u'source', u'individu'),)", 'object_name': 'SourceIndividu', 'db_table': "u'libretto_source_individus'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individu': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sourceindividu_set'", 'to': u"orm['libretto.Individu']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sourceindividu_set'", 'to': u"orm['libretto.Source']"})
        },
        u'libretto.sourcelieu': {
            'Meta': {'unique_together': "((u'source', u'lieu'),)", 'object_name': 'SourceLieu', 'db_table': "u'libretto_source_lieux'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lieu': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sourcelieu_set'", 'to': u"orm['libretto.Lieu']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sourcelieu_set'", 'to': u"orm['libretto.Source']"})
        },
        u'libretto.sourceoeuvre': {
            'Meta': {'unique_together': "((u'source', u'oeuvre'),)", 'object_name': 'SourceOeuvre', 'db_table': "u'libretto_source_oeuvres'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oeuvre': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sourceoeuvre_set'", 'to': u"orm['libretto.Oeuvre']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sourceoeuvre_set'", 'to': u"orm['libretto.Source']"})
        },
        u'libretto.sourcepartie': {
            'Meta': {'unique_together': "((u'source', u'partie'),)", 'object_name': 'SourcePartie', 'db_table': "u'libretto_source_parties'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'partie': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sourcepartie_set'", 'to': u"orm['libretto.Partie']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sourcepartie_set'", 'to': u"orm['libretto.Source']"})
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
        u'libretto.typedecaracteristiquedensemble': {
            'Meta': {'ordering': "(u'classement',)", 'object_name': 'TypeDeCaracteristiqueDEnsemble', '_ormbases': [u'libretto.TypeDeCaracteristique']},
            u'typedecaracteristique_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['libretto.TypeDeCaracteristique']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'libretto.typedecaracteristiquedeprogramme': {
            'Meta': {'ordering': "(u'classement',)", 'object_name': 'TypeDeCaracteristiqueDeProgramme', '_ormbases': [u'libretto.TypeDeCaracteristique']},
            u'typedecaracteristique_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['libretto.TypeDeCaracteristique']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'libretto.typedecaracteristiquedoeuvre': {
            'Meta': {'ordering': "(u'classement',)", 'object_name': 'TypeDeCaracteristiqueDOeuvre', '_ormbases': [u'libretto.TypeDeCaracteristique']},
            u'typedecaracteristique_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['libretto.TypeDeCaracteristique']", 'unique': 'True', 'primary_key': 'True'})
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
        },
        u'libretto.typedepersonnel': {
            'Meta': {'ordering': "(u'nom',)", 'object_name': 'TypeDePersonnel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'typedepersonnel'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"})
        },
        u'libretto.typedesource': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'TypeDeSource'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'typedesource'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.HierarchicUser']"}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'get_slug'"})
        }
    }

    complete_apps = ['libretto']
    symmetrical = True
