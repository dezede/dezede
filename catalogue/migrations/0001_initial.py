# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Document'
        db.create_table('catalogue_document', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('document', self.gf('filebrowser.fields.FileBrowseField')(max_length=400)),
            ('description', self.gf('tinymce.models.HTMLField')(blank=True)),
        ))
        db.send_create_signal('catalogue', ['Document'])

        # Adding model 'Illustration'
        db.create_table('catalogue_illustration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('legende', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('image', self.gf('filebrowser.fields.FileBrowseField')(max_length=400)),
            ('commentaire', self.gf('tinymce.models.HTMLField')(blank=True)),
        ))
        db.send_create_signal('catalogue', ['Illustration'])

        # Adding model 'Etat'
        db.create_table('catalogue_etat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('nom_pluriel', self.gf('django.db.models.fields.CharField')(max_length=230, blank=True)),
            ('message', self.gf('tinymce.models.HTMLField')(blank=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from=None)),
        ))
        db.send_create_signal('catalogue', ['Etat'])

        # Adding model 'NatureDeLieu'
        db.create_table('catalogue_naturedelieu', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from=None)),
            ('nom', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('nom_pluriel', self.gf('django.db.models.fields.CharField')(max_length=430, blank=True)),
            ('referent', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('catalogue', ['NatureDeLieu'])

        # Adding model 'Lieu'
        db.create_table('catalogue_lieu', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('etat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True, blank=True)),
            ('notes', self.gf('tinymce.models.HTMLField')(blank=True)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=50, populate_from=None, unique_with=())),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='enfant', null=True, to=orm['catalogue.Lieu'])),
            ('nature', self.gf('django.db.models.fields.related.ForeignKey')(related_name='lieux', to=orm['catalogue.NatureDeLieu'])),
            ('historique', self.gf('tinymce.models.HTMLField')(blank=True)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('catalogue', ['Lieu'])

        # Adding unique constraint on 'Lieu', fields ['nom', 'parent']
        db.create_unique('catalogue_lieu', ['nom', 'parent_id'])

        # Adding M2M table for field documents on 'Lieu'
        db.create_table('catalogue_lieu_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('lieu', models.ForeignKey(orm['catalogue.lieu'], null=False)),
            ('document', models.ForeignKey(orm['catalogue.document'], null=False))
        ))
        db.create_unique('catalogue_lieu_documents', ['lieu_id', 'document_id'])

        # Adding M2M table for field illustrations on 'Lieu'
        db.create_table('catalogue_lieu_illustrations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('lieu', models.ForeignKey(orm['catalogue.lieu'], null=False)),
            ('illustration', models.ForeignKey(orm['catalogue.illustration'], null=False))
        ))
        db.create_unique('catalogue_lieu_illustrations', ['lieu_id', 'illustration_id'])

        # Adding model 'Saison'
        db.create_table('catalogue_saison', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('lieu', self.gf('django.db.models.fields.related.ForeignKey')(related_name='saisons', to=orm['catalogue.Lieu'])),
            ('debut', self.gf('django.db.models.fields.DateField')()),
            ('fin', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('catalogue', ['Saison'])

        # Adding model 'AncrageSpatioTemporel'
        db.create_table('catalogue_ancragespatiotemporel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('heure', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('lieu', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ancrages', null=True, to=orm['catalogue.Lieu'])),
            ('date_approx', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('heure_approx', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('lieu_approx', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('catalogue', ['AncrageSpatioTemporel'])

        # Adding model 'Prenom'
        db.create_table('catalogue_prenom', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('prenom', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('classement', self.gf('django.db.models.fields.FloatField')(default=1.0)),
            ('favori', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('catalogue', ['Prenom'])

        # Adding model 'TypeDeParenteDIndividus'
        db.create_table('catalogue_typedeparentedindividus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('nom_pluriel', self.gf('django.db.models.fields.CharField')(max_length=55, blank=True)),
            ('classement', self.gf('django.db.models.fields.FloatField')(default=1.0)),
        ))
        db.send_create_signal('catalogue', ['TypeDeParenteDIndividus'])

        # Adding model 'ParenteDIndividus'
        db.create_table('catalogue_parentedindividus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parentes', to=orm['catalogue.TypeDeParenteDIndividus'])),
        ))
        db.send_create_signal('catalogue', ['ParenteDIndividus'])

        # Adding M2M table for field individus_cibles on 'ParenteDIndividus'
        db.create_table('catalogue_parentedindividus_individus_cibles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('parentedindividus', models.ForeignKey(orm['catalogue.parentedindividus'], null=False)),
            ('individu', models.ForeignKey(orm['catalogue.individu'], null=False))
        ))
        db.create_unique('catalogue_parentedindividus_individus_cibles', ['parentedindividus_id', 'individu_id'])

        # Adding model 'Individu'
        db.create_table('catalogue_individu', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('etat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True, blank=True)),
            ('notes', self.gf('tinymce.models.HTMLField')(blank=True)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=50, populate_from=None, unique_with=())),
            ('particule_nom', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('particule_nom_naissance', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('nom_naissance', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('pseudonyme', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('designation', self.gf('django.db.models.fields.CharField')(default='S', max_length=1)),
            ('titre', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('ancrage_naissance', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='individus_nes', unique=True, null=True, to=orm['catalogue.AncrageSpatioTemporel'])),
            ('ancrage_deces', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='individus_decedes', unique=True, null=True, to=orm['catalogue.AncrageSpatioTemporel'])),
            ('ancrage_approx', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='individus', unique=True, null=True, to=orm['catalogue.AncrageSpatioTemporel'])),
            ('biographie', self.gf('tinymce.models.HTMLField')(blank=True)),
        ))
        db.send_create_signal('catalogue', ['Individu'])

        # Adding M2M table for field documents on 'Individu'
        db.create_table('catalogue_individu_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('individu', models.ForeignKey(orm['catalogue.individu'], null=False)),
            ('document', models.ForeignKey(orm['catalogue.document'], null=False))
        ))
        db.create_unique('catalogue_individu_documents', ['individu_id', 'document_id'])

        # Adding M2M table for field illustrations on 'Individu'
        db.create_table('catalogue_individu_illustrations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('individu', models.ForeignKey(orm['catalogue.individu'], null=False)),
            ('illustration', models.ForeignKey(orm['catalogue.illustration'], null=False))
        ))
        db.create_unique('catalogue_individu_illustrations', ['individu_id', 'illustration_id'])

        # Adding M2M table for field prenoms on 'Individu'
        db.create_table('catalogue_individu_prenoms', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('individu', models.ForeignKey(orm['catalogue.individu'], null=False)),
            ('prenom', models.ForeignKey(orm['catalogue.prenom'], null=False))
        ))
        db.create_unique('catalogue_individu_prenoms', ['individu_id', 'prenom_id'])

        # Adding M2M table for field professions on 'Individu'
        db.create_table('catalogue_individu_professions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('individu', models.ForeignKey(orm['catalogue.individu'], null=False)),
            ('profession', models.ForeignKey(orm['catalogue.profession'], null=False))
        ))
        db.create_unique('catalogue_individu_professions', ['individu_id', 'profession_id'])

        # Adding M2M table for field parentes on 'Individu'
        db.create_table('catalogue_individu_parentes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('individu', models.ForeignKey(orm['catalogue.individu'], null=False)),
            ('parentedindividus', models.ForeignKey(orm['catalogue.parentedindividus'], null=False))
        ))
        db.create_unique('catalogue_individu_parentes', ['individu_id', 'parentedindividus_id'])

        # Adding model 'Profession'
        db.create_table('catalogue_profession', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from=None)),
            ('nom', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('nom_pluriel', self.gf('django.db.models.fields.CharField')(max_length=230, blank=True)),
            ('nom_feminin', self.gf('django.db.models.fields.CharField')(max_length=230, blank=True)),
            ('parente', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='enfant', null=True, to=orm['catalogue.Profession'])),
        ))
        db.send_create_signal('catalogue', ['Profession'])

        # Adding model 'Devise'
        db.create_table('catalogue_devise', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200, blank=True)),
            ('symbole', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
        ))
        db.send_create_signal('catalogue', ['Devise'])

        # Adding model 'Engagement'
        db.create_table('catalogue_engagement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('profession', self.gf('django.db.models.fields.related.ForeignKey')(related_name='engagements', to=orm['catalogue.Profession'])),
            ('salaire', self.gf('django.db.models.fields.FloatField')(blank=True)),
            ('devise', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='engagements', null=True, to=orm['catalogue.Devise'])),
        ))
        db.send_create_signal('catalogue', ['Engagement'])

        # Adding M2M table for field individus on 'Engagement'
        db.create_table('catalogue_engagement_individus', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('engagement', models.ForeignKey(orm['catalogue.engagement'], null=False)),
            ('individu', models.ForeignKey(orm['catalogue.individu'], null=False))
        ))
        db.create_unique('catalogue_engagement_individus', ['engagement_id', 'individu_id'])

        # Adding model 'TypeDePersonnel'
        db.create_table('catalogue_typedepersonnel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('catalogue', ['TypeDePersonnel'])

        # Adding model 'Personnel'
        db.create_table('catalogue_personnel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='personnels', to=orm['catalogue.TypeDePersonnel'])),
            ('saison', self.gf('django.db.models.fields.related.ForeignKey')(related_name='personnels', to=orm['catalogue.Saison'])),
        ))
        db.send_create_signal('catalogue', ['Personnel'])

        # Adding M2M table for field engagements on 'Personnel'
        db.create_table('catalogue_personnel_engagements', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('personnel', models.ForeignKey(orm['catalogue.personnel'], null=False)),
            ('engagement', models.ForeignKey(orm['catalogue.engagement'], null=False))
        ))
        db.create_unique('catalogue_personnel_engagements', ['personnel_id', 'engagement_id'])

        # Adding model 'GenreDOeuvre'
        db.create_table('catalogue_genredoeuvre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from=None)),
            ('nom', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('nom_pluriel', self.gf('django.db.models.fields.CharField')(max_length=430, blank=True)),
        ))
        db.send_create_signal('catalogue', ['GenreDOeuvre'])

        # Adding M2M table for field parents on 'GenreDOeuvre'
        db.create_table('catalogue_genredoeuvre_parents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_genredoeuvre', models.ForeignKey(orm['catalogue.genredoeuvre'], null=False)),
            ('to_genredoeuvre', models.ForeignKey(orm['catalogue.genredoeuvre'], null=False))
        ))
        db.create_unique('catalogue_genredoeuvre_parents', ['from_genredoeuvre_id', 'to_genredoeuvre_id'])

        # Adding model 'TypeDeCaracteristiqueDOeuvre'
        db.create_table('catalogue_typedecaracteristiquedoeuvre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('nom_pluriel', self.gf('django.db.models.fields.CharField')(max_length=230, blank=True)),
            ('classement', self.gf('django.db.models.fields.FloatField')(default=1.0)),
        ))
        db.send_create_signal('catalogue', ['TypeDeCaracteristiqueDOeuvre'])

        # Adding model 'CaracteristiqueDOeuvre'
        db.create_table('catalogue_caracteristiquedoeuvre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='caracteristiques_d_oeuvre', to=orm['catalogue.TypeDeCaracteristiqueDOeuvre'])),
            ('valeur', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('classement', self.gf('django.db.models.fields.FloatField')(default=1.0)),
        ))
        db.send_create_signal('catalogue', ['CaracteristiqueDOeuvre'])

        # Adding model 'Partie'
        db.create_table('catalogue_partie', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from=None)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('nom_pluriel', self.gf('django.db.models.fields.CharField')(max_length=230, blank=True)),
            ('parente', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='enfant', null=True, to=orm['catalogue.Partie'])),
            ('classement', self.gf('django.db.models.fields.FloatField')(default=1.0)),
        ))
        db.send_create_signal('catalogue', ['Partie'])

        # Adding M2M table for field professions on 'Partie'
        db.create_table('catalogue_partie_professions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('partie', models.ForeignKey(orm['catalogue.partie'], null=False)),
            ('profession', models.ForeignKey(orm['catalogue.profession'], null=False))
        ))
        db.create_unique('catalogue_partie_professions', ['partie_id', 'profession_id'])

        # Adding model 'Pupitre'
        db.create_table('catalogue_pupitre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('partie', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pupitres', to=orm['catalogue.Partie'])),
            ('quantite_min', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('quantite_max', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('catalogue', ['Pupitre'])

        # Adding model 'TypeDeParenteDOeuvres'
        db.create_table('catalogue_typedeparentedoeuvres', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('nom_relatif', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('nom_relatif_pluriel', self.gf('django.db.models.fields.CharField')(max_length=130, blank=True)),
            ('classement', self.gf('django.db.models.fields.FloatField')(default=1.0)),
        ))
        db.send_create_signal('catalogue', ['TypeDeParenteDOeuvres'])

        # Adding model 'ParenteDOeuvres'
        db.create_table('catalogue_parentedoeuvres', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parentes', to=orm['catalogue.TypeDeParenteDOeuvres'])),
            ('mere', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parentes_filles', to=orm['catalogue.Oeuvre'])),
            ('fille', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parentes_meres', to=orm['catalogue.Oeuvre'])),
        ))
        db.send_create_signal('catalogue', ['ParenteDOeuvres'])

        # Adding unique constraint on 'ParenteDOeuvres', fields ['type', 'mere', 'fille']
        db.create_unique('catalogue_parentedoeuvres', ['type_id', 'mere_id', 'fille_id'])

        # Adding model 'Auteur'
        db.create_table('catalogue_auteur', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('individu', self.gf('django.db.models.fields.related.ForeignKey')(related_name='auteurs', to=orm['catalogue.Individu'])),
            ('profession', self.gf('django.db.models.fields.related.ForeignKey')(related_name='auteurs', to=orm['catalogue.Profession'])),
        ))
        db.send_create_signal('catalogue', ['Auteur'])

        # Adding model 'Oeuvre'
        db.create_table('catalogue_oeuvre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('etat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True, blank=True)),
            ('notes', self.gf('tinymce.models.HTMLField')(blank=True)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=50, populate_from=None, unique_with=())),
            ('prefixe_titre', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('titre', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('coordination', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('prefixe_titre_secondaire', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('titre_secondaire', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('genre', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='oeuvres', null=True, to=orm['catalogue.GenreDOeuvre'])),
            ('ancrage_creation', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='oeuvres_creees', unique=True, null=True, to=orm['catalogue.AncrageSpatioTemporel'])),
            ('lilypond', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('tinymce.models.HTMLField')(blank=True)),
        ))
        db.send_create_signal('catalogue', ['Oeuvre'])

        # Adding M2M table for field documents on 'Oeuvre'
        db.create_table('catalogue_oeuvre_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('oeuvre', models.ForeignKey(orm['catalogue.oeuvre'], null=False)),
            ('document', models.ForeignKey(orm['catalogue.document'], null=False))
        ))
        db.create_unique('catalogue_oeuvre_documents', ['oeuvre_id', 'document_id'])

        # Adding M2M table for field illustrations on 'Oeuvre'
        db.create_table('catalogue_oeuvre_illustrations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('oeuvre', models.ForeignKey(orm['catalogue.oeuvre'], null=False)),
            ('illustration', models.ForeignKey(orm['catalogue.illustration'], null=False))
        ))
        db.create_unique('catalogue_oeuvre_illustrations', ['oeuvre_id', 'illustration_id'])

        # Adding M2M table for field caracteristiques on 'Oeuvre'
        db.create_table('catalogue_oeuvre_caracteristiques', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('oeuvre', models.ForeignKey(orm['catalogue.oeuvre'], null=False)),
            ('caracteristiquedoeuvre', models.ForeignKey(orm['catalogue.caracteristiquedoeuvre'], null=False))
        ))
        db.create_unique('catalogue_oeuvre_caracteristiques', ['oeuvre_id', 'caracteristiquedoeuvre_id'])

        # Adding M2M table for field pupitres on 'Oeuvre'
        db.create_table('catalogue_oeuvre_pupitres', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('oeuvre', models.ForeignKey(orm['catalogue.oeuvre'], null=False)),
            ('pupitre', models.ForeignKey(orm['catalogue.pupitre'], null=False))
        ))
        db.create_unique('catalogue_oeuvre_pupitres', ['oeuvre_id', 'pupitre_id'])

        # Adding model 'AttributionDePupitre'
        db.create_table('catalogue_attributiondepupitre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('pupitre', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attributions_de_pupitre', to=orm['catalogue.Pupitre'])),
        ))
        db.send_create_signal('catalogue', ['AttributionDePupitre'])

        # Adding M2M table for field individus on 'AttributionDePupitre'
        db.create_table('catalogue_attributiondepupitre_individus', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('attributiondepupitre', models.ForeignKey(orm['catalogue.attributiondepupitre'], null=False)),
            ('individu', models.ForeignKey(orm['catalogue.individu'], null=False))
        ))
        db.create_unique('catalogue_attributiondepupitre_individus', ['attributiondepupitre_id', 'individu_id'])

        # Adding model 'CaracteristiqueDElementDeProgramme'
        db.create_table('catalogue_caracteristiquedelementdeprogramme', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('nom_pluriel', self.gf('django.db.models.fields.CharField')(max_length=110, blank=True)),
            ('classement', self.gf('django.db.models.fields.FloatField')(default=1.0)),
        ))
        db.send_create_signal('catalogue', ['CaracteristiqueDElementDeProgramme'])

        # Adding model 'ElementDeProgramme'
        db.create_table('catalogue_elementdeprogramme', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('etat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True, blank=True)),
            ('notes', self.gf('tinymce.models.HTMLField')(blank=True)),
            ('evenement', self.gf('django.db.models.fields.related.ForeignKey')(related_name='programme', to=orm['catalogue.Evenement'])),
            ('oeuvre', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='elements_de_programme', null=True, to=orm['catalogue.Oeuvre'])),
            ('autre', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('position', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal('catalogue', ['ElementDeProgramme'])

        # Adding M2M table for field documents on 'ElementDeProgramme'
        db.create_table('catalogue_elementdeprogramme_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('elementdeprogramme', models.ForeignKey(orm['catalogue.elementdeprogramme'], null=False)),
            ('document', models.ForeignKey(orm['catalogue.document'], null=False))
        ))
        db.create_unique('catalogue_elementdeprogramme_documents', ['elementdeprogramme_id', 'document_id'])

        # Adding M2M table for field illustrations on 'ElementDeProgramme'
        db.create_table('catalogue_elementdeprogramme_illustrations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('elementdeprogramme', models.ForeignKey(orm['catalogue.elementdeprogramme'], null=False)),
            ('illustration', models.ForeignKey(orm['catalogue.illustration'], null=False))
        ))
        db.create_unique('catalogue_elementdeprogramme_illustrations', ['elementdeprogramme_id', 'illustration_id'])

        # Adding M2M table for field caracteristiques on 'ElementDeProgramme'
        db.create_table('catalogue_elementdeprogramme_caracteristiques', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('elementdeprogramme', models.ForeignKey(orm['catalogue.elementdeprogramme'], null=False)),
            ('caracteristiquedelementdeprogramme', models.ForeignKey(orm['catalogue.caracteristiquedelementdeprogramme'], null=False))
        ))
        db.create_unique('catalogue_elementdeprogramme_caracteristiques', ['elementdeprogramme_id', 'caracteristiquedelementdeprogramme_id'])

        # Adding M2M table for field distribution on 'ElementDeProgramme'
        db.create_table('catalogue_elementdeprogramme_distribution', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('elementdeprogramme', models.ForeignKey(orm['catalogue.elementdeprogramme'], null=False)),
            ('attributiondepupitre', models.ForeignKey(orm['catalogue.attributiondepupitre'], null=False))
        ))
        db.create_unique('catalogue_elementdeprogramme_distribution', ['elementdeprogramme_id', 'attributiondepupitre_id'])

        # Adding M2M table for field personnels on 'ElementDeProgramme'
        db.create_table('catalogue_elementdeprogramme_personnels', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('elementdeprogramme', models.ForeignKey(orm['catalogue.elementdeprogramme'], null=False)),
            ('personnel', models.ForeignKey(orm['catalogue.personnel'], null=False))
        ))
        db.create_unique('catalogue_elementdeprogramme_personnels', ['elementdeprogramme_id', 'personnel_id'])

        # Adding model 'Evenement'
        db.create_table('catalogue_evenement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('etat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True, blank=True)),
            ('notes', self.gf('tinymce.models.HTMLField')(blank=True)),
            ('ancrage_debut', self.gf('django.db.models.fields.related.OneToOneField')(related_name='evenements_debuts', unique=True, to=orm['catalogue.AncrageSpatioTemporel'])),
            ('ancrage_fin', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='evenements_fins', unique=True, null=True, to=orm['catalogue.AncrageSpatioTemporel'])),
            ('relache', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('circonstance', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
        ))
        db.send_create_signal('catalogue', ['Evenement'])

        # Adding M2M table for field documents on 'Evenement'
        db.create_table('catalogue_evenement_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('evenement', models.ForeignKey(orm['catalogue.evenement'], null=False)),
            ('document', models.ForeignKey(orm['catalogue.document'], null=False))
        ))
        db.create_unique('catalogue_evenement_documents', ['evenement_id', 'document_id'])

        # Adding M2M table for field illustrations on 'Evenement'
        db.create_table('catalogue_evenement_illustrations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('evenement', models.ForeignKey(orm['catalogue.evenement'], null=False)),
            ('illustration', models.ForeignKey(orm['catalogue.illustration'], null=False))
        ))
        db.create_unique('catalogue_evenement_illustrations', ['evenement_id', 'illustration_id'])

        # Adding model 'TypeDeSource'
        db.create_table('catalogue_typedesource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from=None)),
            ('nom', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('nom_pluriel', self.gf('django.db.models.fields.CharField')(max_length=230, blank=True)),
        ))
        db.send_create_signal('catalogue', ['TypeDeSource'])

        # Adding model 'Source'
        db.create_table('catalogue_source', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('etat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True, blank=True)),
            ('notes', self.gf('tinymce.models.HTMLField')(blank=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('numero', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('page', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sources', to=orm['catalogue.TypeDeSource'])),
            ('contenu', self.gf('tinymce.models.HTMLField')(blank=True)),
        ))
        db.send_create_signal('catalogue', ['Source'])

        # Adding M2M table for field documents on 'Source'
        db.create_table('catalogue_source_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('source', models.ForeignKey(orm['catalogue.source'], null=False)),
            ('document', models.ForeignKey(orm['catalogue.document'], null=False))
        ))
        db.create_unique('catalogue_source_documents', ['source_id', 'document_id'])

        # Adding M2M table for field illustrations on 'Source'
        db.create_table('catalogue_source_illustrations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('source', models.ForeignKey(orm['catalogue.source'], null=False)),
            ('illustration', models.ForeignKey(orm['catalogue.illustration'], null=False))
        ))
        db.create_unique('catalogue_source_illustrations', ['source_id', 'illustration_id'])

        # Adding M2M table for field evenements on 'Source'
        db.create_table('catalogue_source_evenements', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('source', models.ForeignKey(orm['catalogue.source'], null=False)),
            ('evenement', models.ForeignKey(orm['catalogue.evenement'], null=False))
        ))
        db.create_unique('catalogue_source_evenements', ['source_id', 'evenement_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ParenteDOeuvres', fields ['type', 'mere', 'fille']
        db.delete_unique('catalogue_parentedoeuvres', ['type_id', 'mere_id', 'fille_id'])

        # Removing unique constraint on 'Lieu', fields ['nom', 'parent']
        db.delete_unique('catalogue_lieu', ['nom', 'parent_id'])

        # Deleting model 'Document'
        db.delete_table('catalogue_document')

        # Deleting model 'Illustration'
        db.delete_table('catalogue_illustration')

        # Deleting model 'Etat'
        db.delete_table('catalogue_etat')

        # Deleting model 'NatureDeLieu'
        db.delete_table('catalogue_naturedelieu')

        # Deleting model 'Lieu'
        db.delete_table('catalogue_lieu')

        # Removing M2M table for field documents on 'Lieu'
        db.delete_table('catalogue_lieu_documents')

        # Removing M2M table for field illustrations on 'Lieu'
        db.delete_table('catalogue_lieu_illustrations')

        # Deleting model 'Saison'
        db.delete_table('catalogue_saison')

        # Deleting model 'AncrageSpatioTemporel'
        db.delete_table('catalogue_ancragespatiotemporel')

        # Deleting model 'Prenom'
        db.delete_table('catalogue_prenom')

        # Deleting model 'TypeDeParenteDIndividus'
        db.delete_table('catalogue_typedeparentedindividus')

        # Deleting model 'ParenteDIndividus'
        db.delete_table('catalogue_parentedindividus')

        # Removing M2M table for field individus_cibles on 'ParenteDIndividus'
        db.delete_table('catalogue_parentedindividus_individus_cibles')

        # Deleting model 'Individu'
        db.delete_table('catalogue_individu')

        # Removing M2M table for field documents on 'Individu'
        db.delete_table('catalogue_individu_documents')

        # Removing M2M table for field illustrations on 'Individu'
        db.delete_table('catalogue_individu_illustrations')

        # Removing M2M table for field prenoms on 'Individu'
        db.delete_table('catalogue_individu_prenoms')

        # Removing M2M table for field professions on 'Individu'
        db.delete_table('catalogue_individu_professions')

        # Removing M2M table for field parentes on 'Individu'
        db.delete_table('catalogue_individu_parentes')

        # Deleting model 'Profession'
        db.delete_table('catalogue_profession')

        # Deleting model 'Devise'
        db.delete_table('catalogue_devise')

        # Deleting model 'Engagement'
        db.delete_table('catalogue_engagement')

        # Removing M2M table for field individus on 'Engagement'
        db.delete_table('catalogue_engagement_individus')

        # Deleting model 'TypeDePersonnel'
        db.delete_table('catalogue_typedepersonnel')

        # Deleting model 'Personnel'
        db.delete_table('catalogue_personnel')

        # Removing M2M table for field engagements on 'Personnel'
        db.delete_table('catalogue_personnel_engagements')

        # Deleting model 'GenreDOeuvre'
        db.delete_table('catalogue_genredoeuvre')

        # Removing M2M table for field parents on 'GenreDOeuvre'
        db.delete_table('catalogue_genredoeuvre_parents')

        # Deleting model 'TypeDeCaracteristiqueDOeuvre'
        db.delete_table('catalogue_typedecaracteristiquedoeuvre')

        # Deleting model 'CaracteristiqueDOeuvre'
        db.delete_table('catalogue_caracteristiquedoeuvre')

        # Deleting model 'Partie'
        db.delete_table('catalogue_partie')

        # Removing M2M table for field professions on 'Partie'
        db.delete_table('catalogue_partie_professions')

        # Deleting model 'Pupitre'
        db.delete_table('catalogue_pupitre')

        # Deleting model 'TypeDeParenteDOeuvres'
        db.delete_table('catalogue_typedeparentedoeuvres')

        # Deleting model 'ParenteDOeuvres'
        db.delete_table('catalogue_parentedoeuvres')

        # Deleting model 'Auteur'
        db.delete_table('catalogue_auteur')

        # Deleting model 'Oeuvre'
        db.delete_table('catalogue_oeuvre')

        # Removing M2M table for field documents on 'Oeuvre'
        db.delete_table('catalogue_oeuvre_documents')

        # Removing M2M table for field illustrations on 'Oeuvre'
        db.delete_table('catalogue_oeuvre_illustrations')

        # Removing M2M table for field caracteristiques on 'Oeuvre'
        db.delete_table('catalogue_oeuvre_caracteristiques')

        # Removing M2M table for field pupitres on 'Oeuvre'
        db.delete_table('catalogue_oeuvre_pupitres')

        # Deleting model 'AttributionDePupitre'
        db.delete_table('catalogue_attributiondepupitre')

        # Removing M2M table for field individus on 'AttributionDePupitre'
        db.delete_table('catalogue_attributiondepupitre_individus')

        # Deleting model 'CaracteristiqueDElementDeProgramme'
        db.delete_table('catalogue_caracteristiquedelementdeprogramme')

        # Deleting model 'ElementDeProgramme'
        db.delete_table('catalogue_elementdeprogramme')

        # Removing M2M table for field documents on 'ElementDeProgramme'
        db.delete_table('catalogue_elementdeprogramme_documents')

        # Removing M2M table for field illustrations on 'ElementDeProgramme'
        db.delete_table('catalogue_elementdeprogramme_illustrations')

        # Removing M2M table for field caracteristiques on 'ElementDeProgramme'
        db.delete_table('catalogue_elementdeprogramme_caracteristiques')

        # Removing M2M table for field distribution on 'ElementDeProgramme'
        db.delete_table('catalogue_elementdeprogramme_distribution')

        # Removing M2M table for field personnels on 'ElementDeProgramme'
        db.delete_table('catalogue_elementdeprogramme_personnels')

        # Deleting model 'Evenement'
        db.delete_table('catalogue_evenement')

        # Removing M2M table for field documents on 'Evenement'
        db.delete_table('catalogue_evenement_documents')

        # Removing M2M table for field illustrations on 'Evenement'
        db.delete_table('catalogue_evenement_illustrations')

        # Deleting model 'TypeDeSource'
        db.delete_table('catalogue_typedesource')

        # Deleting model 'Source'
        db.delete_table('catalogue_source')

        # Removing M2M table for field documents on 'Source'
        db.delete_table('catalogue_source_documents')

        # Removing M2M table for field illustrations on 'Source'
        db.delete_table('catalogue_source_illustrations')

        # Removing M2M table for field evenements on 'Source'
        db.delete_table('catalogue_source_evenements')


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
            'Meta': {'ordering': "['titre', 'genre', 'slug']", 'object_name': 'Oeuvre'},
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