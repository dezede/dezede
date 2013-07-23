# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


def migrate_fk(table, field='owner_id', to_table='accounts_hierarchicuser',
               to_field='id'):
    db.delete_foreign_key(table, field)
    sql = db.foreign_key_sql(table, field,
                             to_table, to_field)
    db.execute(sql)


class Migration(SchemaMigration):
    depends_on = (
        ('libretto', '0031_migrate_lieux_et_institutions'),
        ('dossiers', '0004_auto__chg_field_dossierdevenements_etat'),
    )

    def forwards(self, orm):
        migrate_fk('dossiers_dossierdevenements')

        try:
            migrate_fk('django_admin_log', 'user_id')
        except ValueError:
            pass  # django_admin_log is not using South, thus it creates
                  # a relation to HierarchicUser on new databases.

        migrate_fk('libretto_ancragespatiotemporel')
        migrate_fk('libretto_auteur')
        migrate_fk('libretto_caracteristiquedelementdeprogramme')
        migrate_fk('libretto_caracteristique')
        migrate_fk('libretto_devise')
        migrate_fk('libretto_document')
        migrate_fk('libretto_elementdedistribution')
        migrate_fk('libretto_elementdeprogramme')
        migrate_fk('libretto_engagement')
        migrate_fk('libretto_etat')
        migrate_fk('libretto_evenement')
        migrate_fk('libretto_genredoeuvre')
        migrate_fk('libretto_illustration')
        migrate_fk('libretto_individu')
        migrate_fk('libretto_lieu')
        migrate_fk('libretto_naturedelieu')
        migrate_fk('libretto_oeuvre')
        migrate_fk('libretto_parentedindividus')
        migrate_fk('libretto_parentedoeuvres')
        migrate_fk('libretto_partie')
        migrate_fk('libretto_personnel')
        migrate_fk('libretto_prenom')
        migrate_fk('libretto_profession')
        migrate_fk('libretto_pupitre')
        migrate_fk('libretto_saison')
        migrate_fk('libretto_source')
        migrate_fk('libretto_typedecaracteristique')
        migrate_fk('libretto_typedeparente')
        migrate_fk('libretto_typedepersonnel')
        migrate_fk('libretto_typedesource')

        try:
            migrate_fk('registration_registrationprofile', 'user_id')
        except ValueError:
            pass  # registration_registrationprofile is not using South,
            # thus it creates a relation to HierarchicUser on new databases.

        migrate_fk('reversion_revision', 'user_id')

    def backwards(self, orm):
        raise RuntimeError('Cannot reverse this migration.')

    models = {
        u'accounts.hierarchicuser': {
            'Meta': {'object_name': 'HierarchicUser'},
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
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'mentor': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'disciples'", 'null': 'True', 'to': u"orm['accounts.HierarchicUser']"}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
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
        }
    }

    complete_apps = ['accounts']