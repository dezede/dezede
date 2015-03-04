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

        # Changing field 'ParenteDIndividus.owner'
        db.alter_column(u'catalogue_parentedindividus', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'ParenteDIndividus.parent'
        db.alter_column(u'catalogue_parentedindividus', 'parent_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.PROTECT, to=orm['catalogue.Individu']))

        # Changing field 'ParenteDIndividus.type'
        db.alter_column(u'catalogue_parentedindividus', 'type_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.PROTECT, to=orm['catalogue.TypeDeParenteDIndividus']))

        # Changing field 'ParenteDIndividus.enfant'
        db.alter_column(u'catalogue_parentedindividus', 'enfant_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.PROTECT, to=orm['catalogue.Individu']))

        # Changing field 'TypeDeSource.owner'
        db.alter_column(u'catalogue_typedesource', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Document.owner'
        db.alter_column(u'catalogue_document', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'TypeDePersonnel.owner'
        db.alter_column(u'catalogue_typedepersonnel', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Profession.etat'
        db.alter_column(u'catalogue_profession', 'etat_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True, on_delete=models.PROTECT))

        # Changing field 'Profession.owner'
        db.alter_column(u'catalogue_profession', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Saison.owner'
        db.alter_column(u'catalogue_saison', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'CaracteristiqueDOeuvre.owner'
        db.alter_column(u'catalogue_caracteristiquedoeuvre', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'CaracteristiqueDOeuvre.type'
        db.alter_column(u'catalogue_caracteristiquedoeuvre', 'type_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.PROTECT, to=orm['catalogue.TypeDeCaracteristiqueDOeuvre']))

        # Changing field 'NatureDeLieu.owner'
        db.alter_column(u'catalogue_naturedelieu', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'ElementDeDistribution.profession'
        db.alter_column(u'catalogue_elementdedistribution', 'profession_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.PROTECT, to=orm['catalogue.Profession']))

        # Changing field 'ElementDeDistribution.content_type'
        db.alter_column(u'catalogue_elementdedistribution', 'content_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, on_delete=models.PROTECT))

        # Changing field 'ElementDeDistribution.owner'
        db.alter_column(u'catalogue_elementdedistribution', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'ElementDeDistribution.pupitre'
        db.alter_column(u'catalogue_elementdedistribution', 'pupitre_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.PROTECT, to=orm['catalogue.Pupitre']))

        # Changing field 'Prenom.owner'
        db.alter_column(u'catalogue_prenom', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Pupitre.owner'
        db.alter_column(u'catalogue_pupitre', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Pupitre.partie'
        db.alter_column(u'catalogue_pupitre', 'partie_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.PROTECT, to=orm['catalogue.Partie']))

        # Changing field 'ElementDeProgramme.etat'
        db.alter_column(u'catalogue_elementdeprogramme', 'etat_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True, on_delete=models.PROTECT))

        # Changing field 'ElementDeProgramme.oeuvre'
        db.alter_column(u'catalogue_elementdeprogramme', 'oeuvre_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.PROTECT, to=orm['catalogue.Oeuvre']))

        # Changing field 'ElementDeProgramme.owner'
        db.alter_column(u'catalogue_elementdeprogramme', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'TypeDeParenteDOeuvres.owner'
        db.alter_column(u'catalogue_typedeparentedoeuvres', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Partie.etat'
        db.alter_column(u'catalogue_partie', 'etat_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True, on_delete=models.PROTECT))

        # Changing field 'Partie.owner'
        db.alter_column(u'catalogue_partie', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Source.etat'
        db.alter_column(u'catalogue_source', 'etat_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True, on_delete=models.PROTECT))

        # Changing field 'Source.owner'
        db.alter_column(u'catalogue_source', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Source.type'
        db.alter_column(u'catalogue_source', 'type_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.PROTECT, to=orm['catalogue.TypeDeSource']))

        # Changing field 'Devise.owner'
        db.alter_column(u'catalogue_devise', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'TypeDeCaracteristiqueDOeuvre.owner'
        db.alter_column(u'catalogue_typedecaracteristiquedoeuvre', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Personnel.owner'
        db.alter_column(u'catalogue_personnel', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Personnel.type'
        db.alter_column(u'catalogue_personnel', 'type_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.PROTECT, to=orm['catalogue.TypeDePersonnel']))

        # Changing field 'Personnel.saison'
        db.alter_column(u'catalogue_personnel', 'saison_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.PROTECT, to=orm['catalogue.Saison']))

        # Changing field 'CaracteristiqueDElementDeProgramme.owner'
        db.alter_column(u'catalogue_caracteristiquedelementdeprogramme', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Individu.etat'
        db.alter_column(u'catalogue_individu', 'etat_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True, on_delete=models.PROTECT))

        # Changing field 'Individu.owner'
        db.alter_column(u'catalogue_individu', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Engagement.owner'
        db.alter_column(u'catalogue_engagement', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Engagement.devise'
        db.alter_column(u'catalogue_engagement', 'devise_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.PROTECT, to=orm['catalogue.Devise']))

        # Changing field 'Engagement.profession'
        db.alter_column(u'catalogue_engagement', 'profession_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.PROTECT, to=orm['catalogue.Profession']))

        # Changing field 'Oeuvre.etat'
        db.alter_column(u'catalogue_oeuvre', 'etat_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True, on_delete=models.PROTECT))

        # Changing field 'Oeuvre.owner'
        db.alter_column(u'catalogue_oeuvre', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Oeuvre.genre'
        db.alter_column(u'catalogue_oeuvre', 'genre_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.PROTECT, to=orm['catalogue.GenreDOeuvre']))

        # Changing field 'Lieu.etat'
        db.alter_column(u'catalogue_lieu', 'etat_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True, on_delete=models.PROTECT))

        # Changing field 'Lieu.nature'
        db.alter_column(u'catalogue_lieu', 'nature_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.PROTECT, to=orm['catalogue.NatureDeLieu']))

        # Changing field 'Lieu.owner'
        db.alter_column(u'catalogue_lieu', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'GenreDOeuvre.owner'
        db.alter_column(u'catalogue_genredoeuvre', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'TypeDeParenteDIndividus.owner'
        db.alter_column(u'catalogue_typedeparentedindividus', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Etat.owner'
        db.alter_column(u'catalogue_etat', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Evenement.etat'
        db.alter_column(u'catalogue_evenement', 'etat_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True, on_delete=models.PROTECT))

        # Changing field 'Evenement.owner'
        db.alter_column(u'catalogue_evenement', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Illustration.owner'
        db.alter_column(u'catalogue_illustration', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'Auteur.content_type'
        db.alter_column(u'catalogue_auteur', 'content_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], on_delete=models.PROTECT))

        # Changing field 'Auteur.owner'
        db.alter_column(u'catalogue_auteur', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'AncrageSpatioTemporel.owner'
        db.alter_column(u'catalogue_ancragespatiotemporel', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'ParenteDOeuvres.owner'
        db.alter_column(u'catalogue_parentedoeuvres', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT))

        # Changing field 'ParenteDOeuvres.type'
        db.alter_column(u'catalogue_parentedoeuvres', 'type_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.PROTECT, to=orm['catalogue.TypeDeParenteDOeuvres']))

    def backwards(self, orm):

        # Changing field 'ParenteDIndividus.owner'
        db.alter_column(u'catalogue_parentedindividus', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'ParenteDIndividus.parent'
        db.alter_column(u'catalogue_parentedindividus', 'parent_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Individu']))

        # Changing field 'ParenteDIndividus.type'
        db.alter_column(u'catalogue_parentedindividus', 'type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.TypeDeParenteDIndividus']))

        # Changing field 'ParenteDIndividus.enfant'
        db.alter_column(u'catalogue_parentedindividus', 'enfant_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Individu']))

        # Changing field 'TypeDeSource.owner'
        db.alter_column(u'catalogue_typedesource', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Document.owner'
        db.alter_column(u'catalogue_document', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'TypeDePersonnel.owner'
        db.alter_column(u'catalogue_typedepersonnel', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Profession.etat'
        db.alter_column(u'catalogue_profession', 'etat_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True))

        # Changing field 'Profession.owner'
        db.alter_column(u'catalogue_profession', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Saison.owner'
        db.alter_column(u'catalogue_saison', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'CaracteristiqueDOeuvre.owner'
        db.alter_column(u'catalogue_caracteristiquedoeuvre', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'CaracteristiqueDOeuvre.type'
        db.alter_column(u'catalogue_caracteristiquedoeuvre', 'type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.TypeDeCaracteristiqueDOeuvre']))

        # Changing field 'NatureDeLieu.owner'
        db.alter_column(u'catalogue_naturedelieu', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'ElementDeDistribution.profession'
        db.alter_column(u'catalogue_elementdedistribution', 'profession_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['catalogue.Profession']))

        # Changing field 'ElementDeDistribution.content_type'
        db.alter_column(u'catalogue_elementdedistribution', 'content_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True))

        # Changing field 'ElementDeDistribution.owner'
        db.alter_column(u'catalogue_elementdedistribution', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'ElementDeDistribution.pupitre'
        db.alter_column(u'catalogue_elementdedistribution', 'pupitre_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['catalogue.Pupitre']))

        # Changing field 'Prenom.owner'
        db.alter_column(u'catalogue_prenom', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Pupitre.owner'
        db.alter_column(u'catalogue_pupitre', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Pupitre.partie'
        db.alter_column(u'catalogue_pupitre', 'partie_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Partie']))

        # Changing field 'ElementDeProgramme.etat'
        db.alter_column(u'catalogue_elementdeprogramme', 'etat_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True))

        # Changing field 'ElementDeProgramme.oeuvre'
        db.alter_column(u'catalogue_elementdeprogramme', 'oeuvre_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['catalogue.Oeuvre']))

        # Changing field 'ElementDeProgramme.owner'
        db.alter_column(u'catalogue_elementdeprogramme', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'TypeDeParenteDOeuvres.owner'
        db.alter_column(u'catalogue_typedeparentedoeuvres', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Partie.etat'
        db.alter_column(u'catalogue_partie', 'etat_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True))

        # Changing field 'Partie.owner'
        db.alter_column(u'catalogue_partie', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Source.etat'
        db.alter_column(u'catalogue_source', 'etat_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True))

        # Changing field 'Source.owner'
        db.alter_column(u'catalogue_source', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Source.type'
        db.alter_column(u'catalogue_source', 'type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.TypeDeSource']))

        # Changing field 'Devise.owner'
        db.alter_column(u'catalogue_devise', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'TypeDeCaracteristiqueDOeuvre.owner'
        db.alter_column(u'catalogue_typedecaracteristiquedoeuvre', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Personnel.owner'
        db.alter_column(u'catalogue_personnel', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Personnel.type'
        db.alter_column(u'catalogue_personnel', 'type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.TypeDePersonnel']))

        # Changing field 'Personnel.saison'
        db.alter_column(u'catalogue_personnel', 'saison_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Saison']))

        # Changing field 'CaracteristiqueDElementDeProgramme.owner'
        db.alter_column(u'catalogue_caracteristiquedelementdeprogramme', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Individu.etat'
        db.alter_column(u'catalogue_individu', 'etat_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True))

        # Changing field 'Individu.owner'
        db.alter_column(u'catalogue_individu', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Engagement.owner'
        db.alter_column(u'catalogue_engagement', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Engagement.devise'
        db.alter_column(u'catalogue_engagement', 'devise_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['catalogue.Devise']))

        # Changing field 'Engagement.profession'
        db.alter_column(u'catalogue_engagement', 'profession_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Profession']))

        # Changing field 'Oeuvre.etat'
        db.alter_column(u'catalogue_oeuvre', 'etat_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True))

        # Changing field 'Oeuvre.owner'
        db.alter_column(u'catalogue_oeuvre', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Oeuvre.genre'
        db.alter_column(u'catalogue_oeuvre', 'genre_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['catalogue.GenreDOeuvre']))

        # Changing field 'Lieu.etat'
        db.alter_column(u'catalogue_lieu', 'etat_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True))

        # Changing field 'Lieu.nature'
        db.alter_column(u'catalogue_lieu', 'nature_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.NatureDeLieu']))

        # Changing field 'Lieu.owner'
        db.alter_column(u'catalogue_lieu', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'GenreDOeuvre.owner'
        db.alter_column(u'catalogue_genredoeuvre', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'TypeDeParenteDIndividus.owner'
        db.alter_column(u'catalogue_typedeparentedindividus', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Etat.owner'
        db.alter_column(u'catalogue_etat', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Evenement.etat'
        db.alter_column(u'catalogue_evenement', 'etat_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Etat'], null=True))

        # Changing field 'Evenement.owner'
        db.alter_column(u'catalogue_evenement', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Illustration.owner'
        db.alter_column(u'catalogue_illustration', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Auteur.content_type'
        db.alter_column(u'catalogue_auteur', 'content_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType']))

        # Changing field 'Auteur.owner'
        db.alter_column(u'catalogue_auteur', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'AncrageSpatioTemporel.owner'
        db.alter_column(u'catalogue_ancragespatiotemporel', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'ParenteDOeuvres.owner'
        db.alter_column(u'catalogue_parentedoeuvres', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'ParenteDOeuvres.type'
        db.alter_column(u'catalogue_parentedoeuvres', 'type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.TypeDeParenteDOeuvres']))

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
            'Meta': {'ordering': "(u'date', u'heure', u'lieu__parent', u'lieu', u'date_approx', u'heure_approx', u'lieu_approx')", 'object_name': 'AncrageSpatioTemporel'},
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'date_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'heure': ('django.db.models.fields.TimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'heure_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lieu': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'ancrages'", 'null': 'True', 'to': u"orm['catalogue.Lieu']"}),
            'lieu_approx': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'catalogue.auteur': {
            'Meta': {'ordering': "(u'profession', u'individu__nom')", 'object_name': 'Auteur'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'on_delete': 'models.PROTECT'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individu': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'auteurs'", 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.Individu']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'auteurs'", 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.Profession']"})
        },
        u'catalogue.caracteristiquedelementdeprogramme': {
            'Meta': {'ordering': "(u'nom',)", 'object_name': 'CaracteristiqueDElementDeProgramme'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '110', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'catalogue.caracteristiquedoeuvre': {
            'Meta': {'ordering': "(u'type', u'classement', u'valeur')", 'object_name': 'CaracteristiqueDOeuvre'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'caracteristiques_d_oeuvre'", 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.TypeDeCaracteristiqueDOeuvre']"}),
            'valeur': ('django.db.models.fields.CharField', [], {'max_length': '400'})
        },
        u'catalogue.devise': {
            'Meta': {'object_name': 'Devise'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '200', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'symbole': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10', 'db_index': 'True'})
        },
        u'catalogue.document': {
            'Meta': {'ordering': "(u'document',)", 'object_name': 'Document'},
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'document': ('filebrowser.fields.FileBrowseField', [], {'max_length': '400'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'catalogue.elementdedistribution': {
            'Meta': {'ordering': "(u'pupitre',)", 'object_name': 'ElementDeDistribution'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individus': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'elements_de_distribution'", 'symmetrical': 'False', 'to': u"orm['catalogue.Individu']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_distribution'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.Profession']"}),
            'pupitre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_distribution'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.Pupitre']"})
        },
        u'catalogue.elementdeprogramme': {
            'Meta': {'ordering': "(u'position', u'oeuvre')", 'object_name': 'ElementDeProgramme'},
            'autre': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '500', 'blank': 'True'}),
            'caracteristiques': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['catalogue.CaracteristiqueDElementDeProgramme']"}),
            'distribution': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['catalogue.ElementDeDistribution']"}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'evenement': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'programme'", 'to': u"orm['catalogue.Evenement']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'numerotation': ('django.db.models.fields.CharField', [], {'default': "u'O'", 'max_length': '1'}),
            'oeuvre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.Oeuvre']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'personnels': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'elements_de_programme'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['catalogue.Personnel']"}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'catalogue.engagement': {
            'Meta': {'object_name': 'Engagement'},
            'devise': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'engagements'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.Devise']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individus': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'engagements'", 'symmetrical': 'False', 'to': u"orm['catalogue.Individu']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'engagements'", 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.Profession']"}),
            'salaire': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'catalogue.etat': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'Etat'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'nom'"})
        },
        u'catalogue.evenement': {
            'Meta': {'ordering': "(u'ancrage_debut',)", 'object_name': 'Evenement'},
            'ancrage_debut': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'evenements_debuts'", 'unique': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.AncrageSpatioTemporel']"}),
            'ancrage_fin': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'evenements_fins'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.AncrageSpatioTemporel']", 'blank': 'True', 'unique': 'True'}),
            'circonstance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '500', 'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'relache': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'})
        },
        u'catalogue.genredoeuvre': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'GenreDOeuvre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '430', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'parents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'enfants'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['catalogue.GenreDOeuvre']"}),
            'referent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'get_slug'"})
        },
        u'catalogue.illustration': {
            'Meta': {'ordering': "(u'image',)", 'object_name': 'Illustration'},
            'commentaire': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('filebrowser.fields.FileBrowseField', [], {'max_length': '400'}),
            'legende': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'catalogue.individu': {
            'Meta': {'ordering': "(u'nom',)", 'object_name': 'Individu'},
            'ancrage_approx': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'individus'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.AncrageSpatioTemporel']", 'blank': 'True', 'unique': 'True'}),
            'ancrage_deces': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'individus_decedes'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.AncrageSpatioTemporel']", 'blank': 'True', 'unique': 'True'}),
            'ancrage_naissance': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'individus_nes'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.AncrageSpatioTemporel']", 'blank': 'True', 'unique': 'True'}),
            'biographie': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'designation': ('django.db.models.fields.CharField', [], {'default': "u'S'", 'max_length': '1'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'enfants': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'parents'", 'symmetrical': 'False', 'through': u"orm['catalogue.ParenteDIndividus']", 'to': u"orm['catalogue.Individu']"}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'nom_naissance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
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
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'historique': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nature': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'lieux'", 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.NatureDeLieu']"}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfants'", 'null': 'True', 'to': u"orm['catalogue.Lieu']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'catalogue.naturedelieu': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'NatureDeLieu'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '430', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'referent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'get_slug'"})
        },
        u'catalogue.oeuvre': {
            'Meta': {'ordering': "(u'titre', u'genre', u'slug')", 'object_name': 'Oeuvre'},
            'ancrage_creation': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'oeuvres_creees'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.AncrageSpatioTemporel']", 'blank': 'True', 'unique': 'True'}),
            'caracteristiques': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'oeuvres'", 'to': u"orm['catalogue.CaracteristiqueDOeuvre']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'contenu_dans': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfants'", 'null': 'True', 'to': u"orm['catalogue.Oeuvre']"}),
            'coordination': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'blank': 'True'}),
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'evenements': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'oeuvres'", 'symmetrical': 'False', 'through': u"orm['catalogue.ElementDeProgramme']", 'to': u"orm['catalogue.Evenement']"}),
            'filles': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'meres'", 'symmetrical': 'False', 'through': u"orm['catalogue.ParenteDOeuvres']", 'to': u"orm['catalogue.Oeuvre']"}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'oeuvres'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.GenreDOeuvre']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lilypond': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
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
            'enfant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes'", 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.Individu']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'enfances'", 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.Individu']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes'", 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.TypeDeParenteDIndividus']"})
        },
        u'catalogue.parentedoeuvres': {
            'Meta': {'ordering': "(u'type',)", 'unique_together': "((u'type', u'mere', u'fille'),)", 'object_name': 'ParenteDOeuvres'},
            'fille': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes_meres'", 'to': u"orm['catalogue.Oeuvre']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mere': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes_filles'", 'to': u"orm['catalogue.Oeuvre']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'parentes'", 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.TypeDeParenteDOeuvres']"})
        },
        u'catalogue.partie': {
            'Meta': {'ordering': "(u'classement', u'nom')", 'object_name': 'Partie'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfant'", 'null': 'True', 'to': u"orm['catalogue.Partie']"}),
            'professions': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'parties'", 'symmetrical': 'False', 'to': u"orm['catalogue.Profession']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'catalogue.personnel': {
            'Meta': {'object_name': 'Personnel'},
            'engagements': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "u'personnels'", 'symmetrical': 'False', 'to': u"orm['catalogue.Engagement']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'saison': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'personnels'", 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.Saison']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'personnels'", 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.TypeDePersonnel']"})
        },
        u'catalogue.prenom': {
            'Meta': {'ordering': "(u'classement', u'prenom')", 'object_name': 'Prenom'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'favori': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'prenom': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        u'catalogue.profession': {
            'Meta': {'ordering': "(u'classement', u'nom')", 'object_name': 'Profession'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_feminin': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'enfant'", 'null': 'True', 'to': u"orm['catalogue.Profession']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'get_slug'", 'unique_with': '()'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'catalogue.pupitre': {
            'Meta': {'ordering': "(u'partie',)", 'object_name': 'Pupitre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'partie': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pupitres'", 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.Partie']"}),
            'quantite_max': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'}),
            'quantite_min': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'})
        },
        u'catalogue.saison': {
            'Meta': {'ordering': "(u'lieu', u'debut')", 'object_name': 'Saison'},
            'debut': ('django.db.models.fields.DateField', [], {}),
            'fin': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lieu': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'saisons'", 'to': u"orm['catalogue.Lieu']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'catalogue.source': {
            'Meta': {'ordering': "(u'date', u'nom', u'numero', u'page', u'type')", 'object_name': 'Source'},
            'contenu': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Document']", 'null': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalogue.Etat']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'evenements': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'sources'", 'to': u"orm['catalogue.Evenement']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalogue.Illustration']", 'null': 'True', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'notes': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'numero': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'sources'", 'on_delete': 'models.PROTECT', 'to': u"orm['catalogue.TypeDeSource']"})
        },
        u'catalogue.typedecaracteristiquedoeuvre': {
            'Meta': {'ordering': "(u'classement',)", 'object_name': 'TypeDeCaracteristiqueDOeuvre'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'catalogue.typedeparentedindividus': {
            'Meta': {'ordering': "(u'classement',)", 'object_name': 'TypeDeParenteDIndividus'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '55', 'blank': 'True'}),
            'nom_relatif': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'nom_relatif_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '55', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'catalogue.typedeparentedoeuvres': {
            'Meta': {'ordering': "(u'classement',)", 'object_name': 'TypeDeParenteDOeuvres'},
            'classement': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'nom_relatif': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'nom_relatif_pluriel': ('django.db.models.fields.CharField', [], {'max_length': '130', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'catalogue.typedepersonnel': {
            'Meta': {'ordering': "(u'nom',)", 'object_name': 'TypeDePersonnel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'catalogue.typedesource': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'TypeDeSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'nom_pluriel': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '230', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
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