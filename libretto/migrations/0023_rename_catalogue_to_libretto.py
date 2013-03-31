# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('catalogue_document', 'libretto_document')
        db.send_create_signal('libretto', ['Document'])

        db.rename_table('catalogue_illustration', 'libretto_illustration')
        db.send_create_signal('libretto', ['Illustration'])

        db.rename_table('catalogue_etat', 'libretto_etat')
        db.send_create_signal('libretto', ['Etat'])

        db.rename_table('catalogue_typedesource', 'libretto_typedesource')
        db.send_create_signal('libretto', ['TypeDeSource'])

        db.rename_table('catalogue_source', 'libretto_source')
        db.send_create_signal('libretto', ['Source'])

        db.rename_table('catalogue_source_documents', 'libretto_source_documents')

        db.rename_table('catalogue_source_illustrations', 'libretto_source_illustrations')

        db.rename_table('catalogue_source_evenements', 'libretto_source_evenements')

        db.rename_table('catalogue_elementdedistribution', 'libretto_elementdedistribution')
        db.send_create_signal('libretto', ['ElementDeDistribution'])

        db.rename_table('catalogue_elementdedistribution_individus', 'libretto_elementdedistribution_individus')

        db.rename_table('catalogue_caracteristiquedelementdeprogramme', 'libretto_caracteristiquedelementdeprogramme')
        db.send_create_signal('libretto', ['CaracteristiqueDElementDeProgramme'])

        db.rename_table('catalogue_elementdeprogramme', 'libretto_elementdeprogramme')
        db.send_create_signal('libretto', ['ElementDeProgramme'])

        db.rename_table('catalogue_elementdeprogramme_documents', 'libretto_elementdeprogramme_documents')

        db.rename_table('catalogue_elementdeprogramme_illustrations', 'libretto_elementdeprogramme_illustrations')

        db.rename_table('catalogue_elementdeprogramme_caracteristiques', 'libretto_elementdeprogramme_caracteristiques')

        db.rename_table('catalogue_elementdeprogramme_distribution', 'libretto_elementdeprogramme_distribution')

        db.rename_table('catalogue_elementdeprogramme_personnels', 'libretto_elementdeprogramme_personnels')

        db.rename_table('catalogue_evenement', 'libretto_evenement')
        db.send_create_signal('libretto', ['Evenement'])

        db.rename_table('catalogue_evenement_documents', 'libretto_evenement_documents')

        db.rename_table('catalogue_evenement_illustrations', 'libretto_evenement_illustrations')

        db.rename_table('catalogue_prenom', 'libretto_prenom')
        db.send_create_signal('libretto', ['Prenom'])

        db.rename_table('catalogue_typedeparentedindividus', 'libretto_typedeparentedindividus')
        db.send_create_signal('libretto', ['TypeDeParenteDIndividus'])

        db.rename_table('catalogue_parentedindividus', 'libretto_parentedindividus')
        db.send_create_signal('libretto', ['ParenteDIndividus'])

        db.rename_table('catalogue_individu', 'libretto_individu')
        db.send_create_signal('libretto', ['Individu'])

        db.rename_table('catalogue_individu_documents', 'libretto_individu_documents')

        db.rename_table('catalogue_individu_illustrations', 'libretto_individu_illustrations')

        db.rename_table('catalogue_individu_prenoms', 'libretto_individu_prenoms')

        db.rename_table('catalogue_individu_professions', 'libretto_individu_professions')

        db.rename_table('catalogue_profession', 'libretto_profession')
        db.send_create_signal('libretto', ['Profession'])

        db.rename_table('catalogue_profession_documents', 'libretto_profession_documents')

        db.rename_table('catalogue_profession_illustrations', 'libretto_profession_illustrations')

        db.rename_table('catalogue_devise', 'libretto_devise')
        db.send_create_signal('libretto', ['Devise'])

        db.rename_table('catalogue_engagement', 'libretto_engagement')
        db.send_create_signal('libretto', ['Engagement'])

        db.rename_table('catalogue_engagement_individus', 'libretto_engagement_individus')

        db.rename_table('catalogue_typedepersonnel', 'libretto_typedepersonnel')
        db.send_create_signal('libretto', ['TypeDePersonnel'])

        db.rename_table('catalogue_personnel', 'libretto_personnel')
        db.send_create_signal('libretto', ['Personnel'])

        db.rename_table('catalogue_personnel_engagements', 'libretto_personnel_engagements')

        db.rename_table('catalogue_genredoeuvre', 'libretto_genredoeuvre')
        db.send_create_signal('libretto', ['GenreDOeuvre'])

        db.rename_table('catalogue_genredoeuvre_parents', 'libretto_genredoeuvre_parents')

        db.rename_table('catalogue_typedecaracteristiquedoeuvre', 'libretto_typedecaracteristiquedoeuvre')
        db.send_create_signal('libretto', ['TypeDeCaracteristiqueDOeuvre'])

        db.rename_table('catalogue_caracteristiquedoeuvre', 'libretto_caracteristiquedoeuvre')
        db.send_create_signal('libretto', ['CaracteristiqueDOeuvre'])

        db.rename_table('catalogue_partie', 'libretto_partie')
        db.send_create_signal('libretto', ['Partie'])

        db.rename_table('catalogue_partie_documents', 'libretto_partie_documents')

        db.rename_table('catalogue_partie_illustrations', 'libretto_partie_illustrations')

        db.rename_table('catalogue_partie_professions', 'libretto_partie_professions')

        db.rename_table('catalogue_pupitre', 'libretto_pupitre')
        db.send_create_signal('libretto', ['Pupitre'])

        db.rename_table('catalogue_typedeparentedoeuvres', 'libretto_typedeparentedoeuvres')
        db.send_create_signal('libretto', ['TypeDeParenteDOeuvres'])

        db.rename_table('catalogue_parentedoeuvres', 'libretto_parentedoeuvres')
        db.send_create_signal('libretto', ['ParenteDOeuvres'])

        db.rename_table('catalogue_auteur', 'libretto_auteur')
        db.send_create_signal('libretto', ['Auteur'])

        db.rename_table('catalogue_oeuvre', 'libretto_oeuvre')
        db.send_create_signal('libretto', ['Oeuvre'])

        db.rename_table('catalogue_oeuvre_documents', 'libretto_oeuvre_documents')

        db.rename_table('catalogue_oeuvre_illustrations', 'libretto_oeuvre_illustrations')

        db.rename_table('catalogue_oeuvre_caracteristiques', 'libretto_oeuvre_caracteristiques')

        db.rename_table('catalogue_oeuvre_pupitres', 'libretto_oeuvre_pupitres')

        db.rename_table('catalogue_naturedelieu', 'libretto_naturedelieu')
        db.send_create_signal('libretto', ['NatureDeLieu'])

        db.rename_table('catalogue_lieu', 'libretto_lieu')
        db.send_create_signal('libretto', ['Lieu'])

        db.rename_table('catalogue_lieu_documents', 'libretto_lieu_documents')

        db.rename_table('catalogue_lieu_illustrations', 'libretto_lieu_illustrations')

        db.rename_table('catalogue_saison', 'libretto_saison')
        db.send_create_signal('libretto', ['Saison'])

        db.rename_table('catalogue_ancragespatiotemporel', 'libretto_ancragespatiotemporel')
        db.send_create_signal('libretto', ['AncrageSpatioTemporel'])


    def backwards(self, orm):
        db.rename_table('libretto_document', 'catalogue_document')

        db.rename_table('libretto_illustration', 'catalogue_illustration')

        db.rename_table('libretto_etat', 'catalogue_etat')

        db.rename_table('libretto_typedesource', 'catalogue_typedesource')

        db.rename_table('libretto_source', 'catalogue_source')

        db.rename_table('libretto_source_documents', 'catalogue_source_documents')

        db.rename_table('libretto_source_illustrations', 'catalogue_source_illustrations')

        db.rename_table('libretto_source_evenements', 'catalogue_source_evenements')

        db.rename_table('libretto_elementdedistribution', 'catalogue_elementdedistribution')

        db.rename_table('libretto_elementdedistribution_individus', 'catalogue_elementdedistribution_individus')

        db.rename_table('libretto_caracteristiquedelementdeprogramme', 'catalogue_caracteristiquedelementdeprogramme')

        db.rename_table('libretto_elementdeprogramme', 'catalogue_elementdeprogramme')

        db.rename_table('libretto_elementdeprogramme_documents', 'catalogue_elementdeprogramme_documents')

        db.rename_table('libretto_elementdeprogramme_illustrations', 'catalogue_elementdeprogramme_illustrations')

        db.rename_table('libretto_elementdeprogramme_caracteristiques', 'catalogue_elementdeprogramme_caracteristiques')

        db.rename_table('libretto_elementdeprogramme_distribution', 'catalogue_elementdeprogramme_distribution')

        db.rename_table('libretto_elementdeprogramme_personnels', 'catalogue_elementdeprogramme_personnels')

        db.rename_table('libretto_evenement', 'catalogue_evenement')

        db.rename_table('libretto_evenement_documents', 'catalogue_evenement_documents')

        db.rename_table('libretto_evenement_illustrations', 'catalogue_evenement_illustrations')

        db.rename_table('libretto_prenom', 'catalogue_prenom')

        db.rename_table('libretto_typedeparentedindividus', 'catalogue_typedeparentedindividus')

        db.rename_table('libretto_parentedindividus', 'catalogue_parentedindividus')

        db.rename_table('libretto_individu', 'catalogue_individu')

        db.rename_table('libretto_individu_documents', 'catalogue_individu_documents')

        db.rename_table('libretto_individu_illustrations', 'catalogue_individu_illustrations')

        db.rename_table('libretto_individu_prenoms', 'catalogue_individu_prenoms')

        db.rename_table('libretto_individu_professions', 'catalogue_individu_professions')

        db.rename_table('libretto_profession', 'catalogue_profession')

        db.rename_table('libretto_profession_documents', 'catalogue_profession_documents')

        db.rename_table('libretto_profession_illustrations', 'catalogue_profession_illustrations')

        db.rename_table('libretto_devise', 'catalogue_devise')

        db.rename_table('libretto_engagement', 'catalogue_engagement')

        db.rename_table('libretto_engagement_individus', 'catalogue_engagement_individus')

        db.rename_table('libretto_typedepersonnel', 'catalogue_typedepersonnel')

        db.rename_table('libretto_personnel', 'catalogue_personnel')

        db.rename_table('libretto_personnel_engagements', 'catalogue_personnel_engagements')

        db.rename_table('libretto_genredoeuvre', 'catalogue_genredoeuvre')

        db.rename_table('libretto_genredoeuvre_parents', 'catalogue_genredoeuvre_parents')

        db.rename_table('libretto_typedecaracteristiquedoeuvre', 'catalogue_typedecaracteristiquedoeuvre')

        db.rename_table('libretto_caracteristiquedoeuvre', 'catalogue_caracteristiquedoeuvre')

        db.rename_table('libretto_partie', 'catalogue_partie')

        db.rename_table('libretto_partie_documents', 'catalogue_partie_documents')

        db.rename_table('libretto_partie_illustrations', 'catalogue_partie_illustrations')

        db.rename_table('libretto_partie_professions', 'catalogue_partie_professions')

        db.rename_table('libretto_pupitre', 'catalogue_pupitre')

        db.rename_table('libretto_typedeparentedoeuvres', 'catalogue_typedeparentedoeuvres')

        db.rename_table('libretto_parentedoeuvres', 'catalogue_parentedoeuvres')

        db.rename_table('libretto_auteur', 'catalogue_auteur')

        db.rename_table('libretto_oeuvre', 'catalogue_oeuvre')

        db.rename_table('libretto_oeuvre_documents', 'catalogue_oeuvre_documents')

        db.rename_table('libretto_oeuvre_illustrations', 'catalogue_oeuvre_illustrations')

        db.rename_table('libretto_oeuvre_caracteristiques', 'catalogue_oeuvre_caracteristiques')

        db.rename_table('libretto_oeuvre_pupitres', 'catalogue_oeuvre_pupitres')

        db.rename_table('libretto_naturedelieu', 'catalogue_naturedelieu')

        db.rename_table('libretto_lieu', 'catalogue_lieu')

        db.rename_table('libretto_lieu_documents', 'catalogue_lieu_documents')

        db.rename_table('libretto_lieu_illustrations', 'catalogue_lieu_illustrations')

        db.rename_table('libretto_saison', 'catalogue_saison')

        db.rename_table('libretto_ancragespatiotemporel', 'catalogue_ancragespatiotemporel')


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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'libretto.ancragespatiotemporel': {
            'Meta': {'ordering': "(u'date', u'heure', u'lieu__parent', u'lieu', u'date_approx', u'heure_approx', u'lieu_approx')", 'object_name': 'AncrageSpatioTemporel'},
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'date_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'heure': ('django.db.models.fields.TimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'heure_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lieu': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'ancrages'", 'null': 'True', 'to': u"orm['libretto.Lieu']"}),
            'lieu_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'libretto.auteur': {
            'Meta': {'ordering': "(u'profession', u'individu__nom')", 'object_name': 'Auteur'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'on_delete': 'models.PROTECT'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individu': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'auteurs'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Individu']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'auteurs'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Profession']"})
        },
        u'libretto.caracteristiquedelementdeprogramme': {
            'Meta': {'ordering': "(u'nom',)", 'object_name': 'CaracteristiqueDElementDeProgramme'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '110', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'libretto.caracteristiquedoeuvre': {
            'Meta': {'ordering': "(u'type', u'classement', u'valeur')", 'object_name': 'CaracteristiqueDOeuvre'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'caracteristiques_d_oeuvre'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.TypeDeCaracteristiqueDOeuvre']"}),
            'valeur': ('django.db.models.fields.CharField', [], {'max_length': '400'})
        },
        u'libretto.devise': {
            'Meta': {'object_name': 'Devise'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '200', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'symbole': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10', 'db_index': 'True'})
        },
        u'libretto.document': {
            'Meta': {'ordering': "(u'document',)", 'object_name': 'Document'},
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'document': ('filebrowser.fields.FileBrowseField', [], {'max_length': '400'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'libretto.elementdedistribution': {
            'Meta': {'ordering': "(u'pupitre',)", 'object_name': 'ElementDeDistribution'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individus': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'elements_de_distribution'", 'symmetrical': 'False', 'to': u"orm['libretto.Individu']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_distribution'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Profession']"}),
            'pupitre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_distribution'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Pupitre']"})
        },
        u'libretto.elementdeprogramme': {
            'Meta': {'ordering': "(u'position', u'oeuvre')", 'object_name': 'ElementDeProgramme'},
            'autre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '500', 'blank': 'True'}),
            'caracteristiques': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.CaracteristiqueDElementDeProgramme']"}),
            'distribution': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.ElementDeDistribution']"}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['libretto.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'evenement': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'programme'", 'to': u"orm['libretto.Evenement']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['libretto.Illustration']", 'null': 'True', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'numerotation': ('django.db.models.fields.CharField', [], {'default': "u'O'", 'max_length': '1'}),
            'oeuvre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Oeuvre']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'personnels': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.Personnel']"}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'libretto.engagement': {
            'Meta': {'object_name': 'Engagement'},
            'devise': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'engagements'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Devise']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individus': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'engagements'", 'symmetrical': 'False', 'to': u"orm['libretto.Individu']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'engagements'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Profession']"}),
            'salaire': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'libretto.etat': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'Etat'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'nom'"})
        },
        u'libretto.evenement': {
            'Meta': {'ordering': "(u'ancrage_debut',)", 'object_name': 'Evenement'},
            'ancrage_debut': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'evenements_debuts'", 'unique': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.AncrageSpatioTemporel']"}),
            'ancrage_fin': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'evenements_fins'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.AncrageSpatioTemporel']", 'blank': 'True', 'unique': 'True'}),
            'circonstance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '500', 'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['libretto.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['libretto.Illustration']", 'null': 'True', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'relache': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'})
        },
        u'libretto.genredoeuvre': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'GenreDOeuvre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '430', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'parents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'enfants'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['libretto.GenreDOeuvre']"}),
            'referent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'get_slug'"})
        },
        u'libretto.illustration': {
            'Meta': {'ordering': "(u'image',)", 'object_name': 'Illustration'},
            'commentaire': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('filebrowser.fields.FileBrowseField', [], {'max_length': '400'}),
            'legende': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'libretto.individu': {
            'Meta': {'ordering': "(u'nom',)", 'object_name': 'Individu'},
            'ancrage_approx': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'individus'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.AncrageSpatioTemporel']", 'blank': 'True', 'unique': 'True'}),
            'ancrage_deces': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'individus_decedes'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.AncrageSpatioTemporel']", 'blank': 'True', 'unique': 'True'}),
            'ancrage_naissance': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'individus_nes'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.AncrageSpatioTemporel']", 'blank': 'True', 'unique': 'True'}),
            'biographie': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'designation': ('django.db.models.fields.CharField', [], {'default': "u'S'", 'max_length': '1'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['libretto.Document']", 'null': 'True', 'blank': 'True'}),
            'enfants': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'parents'", 'symmetrical': 'False', 'through': u"orm['libretto.ParenteDIndividus']", 'to': u"orm['libretto.Individu']"}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['libretto.Illustration']", 'null': 'True', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'nom_naissance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'particule_nom': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'blank': 'True'}),
            'particule_nom_naissance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'blank': 'True'}),
            'prenoms': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'individus'", 'to': u"orm['libretto.Prenom']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'professions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'individus'", 'to': u"orm['libretto.Profession']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'pseudonyme': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'titre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '1', 'blank': 'True'})
        },
        u'libretto.lieu': {
            'Meta': {'ordering': "(u'nom',)", 'unique_together': "((u'nom', u'parent'),)", 'object_name': 'Lieu'},
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['libretto.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'historique': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['libretto.Illustration']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nature': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'lieux'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.NatureDeLieu']"}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfants'", 'null': 'True', 'to': u"orm['libretto.Lieu']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'libretto.naturedelieu': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'NatureDeLieu'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '430', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
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
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['libretto.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'evenements': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'oeuvres'", 'symmetrical': 'False', 'through': u"orm['libretto.ElementDeProgramme']", 'to': u"orm['libretto.Evenement']"}),
            'filles': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'meres'", 'symmetrical': 'False', 'through': u"orm['libretto.ParenteDOeuvres']", 'to': u"orm['libretto.Oeuvre']"}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'oeuvres'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.GenreDOeuvre']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['libretto.Illustration']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lilypond': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'prefixe_titre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'blank': 'True'}),
            'prefixe_titre_secondaire': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'blank': 'True'}),
            'pupitres': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'oeuvres'", 'to': u"orm['libretto.Pupitre']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'titre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'titre_secondaire': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'libretto.parentedindividus': {
            'Meta': {'ordering': "(u'type', u'parent', u'enfant')", 'object_name': 'ParenteDIndividus'},
            'enfant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Individu']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'enfances'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Individu']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.TypeDeParenteDIndividus']"})
        },
        u'libretto.parentedoeuvres': {
            'Meta': {'ordering': "(u'type',)", 'unique_together': "((u'type', u'mere', u'fille'),)", 'object_name': 'ParenteDOeuvres'},
            'fille': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes_meres'", 'to': u"orm['libretto.Oeuvre']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mere': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes_filles'", 'to': u"orm['libretto.Oeuvre']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.TypeDeParenteDOeuvres']"})
        },
        u'libretto.partie': {
            'Meta': {'ordering': "(u'classement', u'nom')", 'object_name': 'Partie'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['libretto.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['libretto.Illustration']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfant'", 'null': 'True', 'to': u"orm['libretto.Partie']"}),
            'professions': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'parties'", 'symmetrical': 'False', 'to': u"orm['libretto.Profession']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'libretto.personnel': {
            'Meta': {'object_name': 'Personnel'},
            'engagements': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'personnels'", 'symmetrical': 'False', 'to': u"orm['libretto.Engagement']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'saison': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'personnels'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Saison']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'personnels'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.TypeDePersonnel']"})
        },
        u'libretto.prenom': {
            'Meta': {'ordering': "(u'classement', u'prenom')", 'object_name': 'Prenom'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'favori': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'prenom': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        u'libretto.profession': {
            'Meta': {'ordering': "(u'classement', u'nom')", 'object_name': 'Profession'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['libretto.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['libretto.Illustration']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_feminin': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfant'", 'null': 'True', 'to': u"orm['libretto.Profession']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'libretto.pupitre': {
            'Meta': {'ordering': "(u'partie',)", 'object_name': 'Pupitre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'partie': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pupitres'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.Partie']"}),
            'quantite_max': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'}),
            'quantite_min': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'})
        },
        u'libretto.saison': {
            'Meta': {'ordering': "(u'lieu', u'debut')", 'object_name': 'Saison'},
            'debut': ('django.db.models.fields.DateField', [], {}),
            'fin': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lieu': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'saisons'", 'to': u"orm['libretto.Lieu']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'libretto.source': {
            'Meta': {'ordering': "(u'date', u'nom', u'numero', u'page', u'type')", 'object_name': 'Source'},
            'contenu': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['libretto.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['libretto.Etat']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'evenements': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'sources'", 'to': u"orm['libretto.Evenement']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['libretto.Illustration']", 'null': 'True', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'numero': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sources'", 'on_delete': 'models.PROTECT', 'to': u"orm['libretto.TypeDeSource']"})
        },
        u'libretto.typedecaracteristiquedoeuvre': {
            'Meta': {'ordering': "(u'classement',)", 'object_name': 'TypeDeCaracteristiqueDOeuvre'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'libretto.typedeparentedindividus': {
            'Meta': {'ordering': "(u'classement',)", 'object_name': 'TypeDeParenteDIndividus'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '55', 'blank': 'True'}),
            'nom_relatif': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'nom_relatif_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '55', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'libretto.typedeparentedoeuvres': {
            'Meta': {'ordering': "(u'classement',)", 'object_name': 'TypeDeParenteDOeuvres'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'nom_relatif': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'nom_relatif_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '130', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'libretto.typedepersonnel': {
            'Meta': {'ordering': "(u'nom',)", 'object_name': 'TypeDePersonnel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'libretto.typedesource': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'TypeDeSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'get_slug'"})
        }
    }

    complete_apps = ['libretto']