# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'HierarchicUser.legal_person'
        db.add_column(u'accounts_hierarchicuser', 'legal_person',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'HierarchicUser.content_type'
        db.add_column(u'accounts_hierarchicuser', 'content_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'HierarchicUser.object_id'
        db.add_column(u'accounts_hierarchicuser', 'object_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'HierarchicUser.show_email'
        db.add_column(u'accounts_hierarchicuser', 'show_email',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'HierarchicUser.website'
        db.add_column(u'accounts_hierarchicuser', 'website',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'HierarchicUser.website_verbose'
        db.add_column(u'accounts_hierarchicuser', 'website_verbose',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'HierarchicUser.avatar'
        db.add_column(u'accounts_hierarchicuser', 'avatar',
                      self.gf('filebrowser.fields.FileBrowseField')(max_length=400, null=True, blank=True),
                      keep_default=False)

        # Adding field 'HierarchicUser.presentation'
        db.add_column(u'accounts_hierarchicuser', 'presentation',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'HierarchicUser.fonctions'
        db.add_column(u'accounts_hierarchicuser', 'fonctions',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'HierarchicUser.literature'
        db.add_column(u'accounts_hierarchicuser', 'literature',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'HierarchicUser.legal_person'
        db.delete_column(u'accounts_hierarchicuser', 'legal_person')

        # Deleting field 'HierarchicUser.content_type'
        db.delete_column(u'accounts_hierarchicuser', 'content_type_id')

        # Deleting field 'HierarchicUser.object_id'
        db.delete_column(u'accounts_hierarchicuser', 'object_id')

        # Deleting field 'HierarchicUser.show_email'
        db.delete_column(u'accounts_hierarchicuser', 'show_email')

        # Deleting field 'HierarchicUser.website'
        db.delete_column(u'accounts_hierarchicuser', 'website')

        # Deleting field 'HierarchicUser.website_verbose'
        db.delete_column(u'accounts_hierarchicuser', 'website_verbose')

        # Deleting field 'HierarchicUser.avatar'
        db.delete_column(u'accounts_hierarchicuser', 'avatar')

        # Deleting field 'HierarchicUser.presentation'
        db.delete_column(u'accounts_hierarchicuser', 'presentation')

        # Deleting field 'HierarchicUser.fonctions'
        db.delete_column(u'accounts_hierarchicuser', 'fonctions')

        # Deleting field 'HierarchicUser.literature'
        db.delete_column(u'accounts_hierarchicuser', 'literature')


    models = {
        u'accounts.hierarchicuser': {
            'Meta': {'object_name': 'HierarchicUser'},
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
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'legal_person': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'literature': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'mentor': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'disciples'", 'null': 'True', 'to': u"orm['accounts.HierarchicUser']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'presentation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'show_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
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
        }
    }

    complete_apps = ['accounts']