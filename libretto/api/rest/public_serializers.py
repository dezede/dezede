"""
Public, read-only DRF serializers for the Next.js (musicaLetters) frontend.

Their JSON mirrors the Wagtail-API ``TRelated*`` shapes already consumed by the
frontend (see ``frontend/app/types.ts`` and ``frontend/app/constants.ts``): every
nested entity carries an ``id`` and a ``meta: {type: "libretto.X"}`` envelope plus
the same fields the React "chip" formatters expect, so those components render this
data unchanged.

These are intentionally separate from the admin-flavoured serializers in
``serializers.py`` (which expose ``change_url``/permissions and are unsuitable for
the public frontend).
"""
from collections import OrderedDict

from django.template.defaultfilters import capfirst, filesizeformat
from django.urls import reverse
from django.utils.text import Truncator
from rest_framework import serializers

from ...models import (
    Individu, Ensemble, Lieu, NatureDeLieu, Oeuvre, Partie, Pupitre,
    GenreDOeuvre, Profession, Auteur, CaracteristiqueDeProgramme,
    ElementDeDistribution, ElementDeProgramme, Evenement, Source,
)


class MetaTypeMixin(serializers.Serializer):
    """Adds the ``meta.type`` envelope expected by the React chips."""
    meta = serializers.SerializerMethodField()

    def get_meta(self, obj):
        return {'type': f'{obj._meta.app_label}.{obj._meta.object_name}'}


class EtatMixin(serializers.Serializer):
    """Adds the publication-state (``Etat``) envelope shown on detail pages.

    Mirrors the Django ``include/etat.html`` panel: ``message`` is the optional
    notice; ``public`` lets the frontend flag a non-published (draft) state an
    authenticated editor may be previewing.
    """
    etat = serializers.SerializerMethodField()

    def get_etat(self, obj):
        etat = obj.etat
        if etat is None:
            return None
        return {'nom': etat.nom, 'message': etat.message, 'public': etat.public}


class TypeDeParenteSerializer(serializers.Serializer):
    """The four labels a parenté group heading picks between (see TypeDeParente)."""
    nom = serializers.CharField()
    nom_relatif = serializers.CharField()
    pluriel = serializers.SerializerMethodField()
    relatif_pluriel = serializers.SerializerMethodField()

    def get_pluriel(self, obj):
        return obj.pluriel()

    def get_relatif_pluriel(self, obj):
        return obj.relatif_pluriel()


def group_parentes(parentes, related_attr, serializer_class, context):
    """Group ``parentes`` by ``type`` into ``[{type, entities}]``.

    ``related_attr`` is the side of the relation to expose (``mere``/``fille``
    for works, ``parent``/``enfant`` for persons). Mirrors the Django
    ``{% regroup … by type %}`` blocks; the caller picks the singular/plural and
    direct/relative label off each group's ``type``.
    """
    groups = OrderedDict()
    for parente in parentes:
        type_obj, items = groups.setdefault(
            parente.type_id, (parente.type, []))
        items.append(getattr(parente, related_attr))
    return [
        {
            'type': TypeDeParenteSerializer(type_obj).data,
            'entities': serializer_class(
                items, many=True, context=context).data,
        }
        for type_obj, items in groups.values()
    ]


def grouped_sources(sources, context):
    """Group published ``sources`` by type into ``[{type, sources}]``.

    Mirrors the Django ``include/sources.html`` panel list (the queryset's
    ``group_by_type``): one block per ``TypeDeSource`` — its name pluralised when
    the group holds several sources. Shown at the bottom of every autorité page
    and on each event. ``sources`` must already be published and ordered; pass a
    queryset with ``select_related('type')`` to keep this query-free per group.
    """
    groups = OrderedDict()
    for source in sources:
        groups.setdefault(source.type_id, []).append(source)
    result = []
    for items in groups.values():
        type_obj = items[0].type
        label = type_obj.pluriel() if len(items) > 1 else type_obj.nom
        result.append({
            'type': capfirst(label),
            'sources': SourceRowSerializer(
                items, many=True, context=context).data,
        })
    return result


# Keys added to every detail endpoint by ``AdminLinkMixin`` (and replicated for
# the hand-built dossier detail in ``dossiers/rest.py``).
ADMIN_LINK_FIELDS = (
    'owner', 'is_public', 'can_change', 'can_delete', 'change_url',
    'delete_url',
)


def can_modify(user, obj, action):
    """Whether ``user`` could open the admin ``action`` page for ``obj``.

    Replicates ``libretto.admin.PublishedAdmin.check_user_ownership``: the
    class-level model permission *plus* admin object ownership — a superuser, or a
    user whose hierarchy (``get_descendants(include_self=True)``) contains the
    object's owner. (Object-level ``has_perm(perm, obj=obj)`` can't be used: the
    project's auth backends are ``ModelBackend``-based and ignore ``obj``.)
    """
    if user is None or not user.is_authenticated:
        return False
    perm = f'{obj._meta.app_label}.{action}_{obj._meta.model_name}'
    if not user.has_perm(perm):
        return False
    return user.is_superuser or user.get_descendants(
        include_self=True).filter(pk=obj.owner_id).exists()


def admin_link_data(obj, request):
    """Owner + admin change/delete links for an object's detail JSON.

    Mirrors the Django frontend's ``frontend_admin``/``ownership`` includes:
    ``owner`` is always returned (anonymous visitors still see the author link),
    ``is_public`` drives the "Privé" padlock (mirrors ``routines/lock.html``),
    while ``can_change``/``can_delete`` gate the admin edit/delete links on the
    same object-level ownership the admin enforces. Used by ``AdminLinkMixin`` and
    reused for the hand-built dossier detail.
    """
    base = f'admin:{obj._meta.app_label}_{obj._meta.model_name}'
    owner = obj.owner
    user = getattr(request, 'user', None)
    return {
        'owner': None if owner is None else {
            'username': owner.username, 'str': str(owner),
            'url': owner.get_absolute_url()},
        'is_public': getattr(obj, 'is_public', True),
        'can_change': can_modify(user, obj, 'change'),
        'can_delete': can_modify(user, obj, 'delete'),
        'change_url': reverse(f'{base}_change', args=(obj.pk,)),
        'delete_url': reverse(f'{base}_delete', args=(obj.pk,)),
    }


class AdminLinkMixin(serializers.Serializer):
    """Adds the ``ADMIN_LINK_FIELDS`` (owner + admin links) to a detail serializer.

    Subclasses must append ``ADMIN_LINK_FIELDS`` to their ``Meta.fields``. Apply
    this only to the serializer used by the ``retrieve`` action — never to list/row
    or nested chip serializers (it would add an owner lookup and two permission
    checks per row)."""
    owner = serializers.SerializerMethodField()
    is_public = serializers.SerializerMethodField()
    can_change = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    change_url = serializers.SerializerMethodField()
    delete_url = serializers.SerializerMethodField()

    def _admin_url(self, obj, action):
        return reverse(
            f'admin:{obj._meta.app_label}_{obj._meta.model_name}_{action}',
            args=(obj.pk,))

    def _user(self):
        return getattr(self.context.get('request'), 'user', None)

    def get_owner(self, obj):
        owner = obj.owner
        if owner is None:
            return None
        return {'username': owner.username, 'str': str(owner),
                'url': owner.get_absolute_url()}

    def get_is_public(self, obj):
        return getattr(obj, 'is_public', True)

    def get_can_change(self, obj):
        return can_modify(self._user(), obj, 'change')

    def get_can_delete(self, obj):
        return can_modify(self._user(), obj, 'delete')

    def get_change_url(self, obj):
        return self._admin_url(obj, 'change')

    def get_delete_url(self, obj):
        return self._admin_url(obj, 'delete')


# -- Leaf entities ----------------------------------------------------------

class NatureDeLieuSerializer(serializers.ModelSerializer):
    class Meta:
        model = NatureDeLieu
        fields = ('nom', 'referent')


class PlaceParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lieu
        fields = ('nom',)


class PlaceSerializer(MetaTypeMixin, serializers.ModelSerializer):
    nature = NatureDeLieuSerializer()
    parent = PlaceParentSerializer()

    class Meta:
        model = Lieu
        fields = ('id', 'meta', 'nom', 'nature', 'parent')


class PersonSerializer(MetaTypeMixin, serializers.ModelSerializer):
    titre_display = serializers.CharField(source='get_titre_display')

    class Meta:
        model = Individu
        fields = (
            'id', 'meta', 'particule_nom', 'nom', 'particule_nom_naissance',
            'nom_naissance', 'prenoms', 'prenoms_complets', 'designation',
            'titre', 'titre_display', 'pseudonyme',
            # Plain columns, so every place a person chip is nested gets the
            # tooltip data without extra queries.
            'naissance_date', 'naissance_date_approx',
            'deces_date', 'deces_date_approx',
        )


class EnsembleSerializer(MetaTypeMixin, serializers.ModelSerializer):
    class Meta:
        model = Ensemble
        fields = ('id', 'meta', 'particule_nom', 'nom')


class ProfessionSerializer(MetaTypeMixin, serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ('id', 'meta', 'nom', 'nom_pluriel', 'nom_feminin',
                  'nom_feminin_pluriel')


class GenreSerializer(MetaTypeMixin, serializers.ModelSerializer):
    class Meta:
        model = GenreDOeuvre
        fields = ('id', 'meta', 'nom', 'referent')


class PartSerializer(MetaTypeMixin, serializers.ModelSerializer):
    part_type = serializers.IntegerField(source='type')
    # The stored ``nom_pluriel`` is often blank; expose the computed plural
    # (``Partie.pluriel`` → ``calc_pluriel``) so labels never drop the part name
    # (mirrors Django's ``Partie.html(pluriel=True)``).
    nom_pluriel = serializers.CharField(source='pluriel')
    # ``oeuvre`` is part of the ``TRelatedPart`` shape but is not needed to render
    # a section/role label, so we avoid the (potentially recursive) work payload.
    oeuvre = serializers.SerializerMethodField()

    class Meta:
        model = Partie
        fields = ('id', 'meta', 'nom', 'nom_pluriel', 'part_type', 'oeuvre')

    def get_oeuvre(self, obj):
        return None


class PupitreSerializer(MetaTypeMixin, serializers.ModelSerializer):
    partie = PartSerializer()

    class Meta:
        model = Pupitre
        fields = ('id', 'meta', 'partie', 'soliste', 'quantite_min',
                  'quantite_max', 'facultatif')


class AuteurSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer()
    individu = PersonSerializer()
    ensemble = EnsembleSerializer()

    class Meta:
        model = Auteur
        fields = ('id', 'profession', 'individu', 'ensemble')


class WorkTitleMixin(MetaTypeMixin, serializers.ModelSerializer):
    """The fields the frontend needs to build an œuvre's label (mirroring
    Django's ``Oeuvre.titre_html``): the title parts, the genre, the
    characteristics and the excerpt designation."""
    genre = GenreSerializer()
    # Raw tonalité code (e.g. ``Aa+``); the frontend localises it itself, rather
    # than receiving a French ``get_tonalite_display`` string it cannot translate.
    tonalite = serializers.CharField()
    arrangement = serializers.CharField(source='get_arrangement_display')
    type_extrait = serializers.CharField(source='get_type_extrait_display')
    categorie_type_extrait = serializers.ReadOnlyField()

    TITLE_FIELDS = (
        'id', 'meta', 'prefixe_titre', 'titre', 'coordination',
        'prefixe_titre_secondaire', 'titre_secondaire', 'genre', 'numero',
        'coupe', 'indeterminee', 'incipit', 'tempo', 'tonalite', 'sujet',
        'arrangement', 'surnom', 'nom_courant', 'opus', 'ict',
        'type_extrait', 'categorie_type_extrait', 'numero_extrait',
    )


class WorkAncestorSerializer(WorkTitleMixin):
    """Lean, self-recursive serializer for an œuvre's parent-work chain
    (``extrait_de``), carrying only what a label needs — no authors, sources or
    casting — so the recursion stays cheap."""
    extrait_de = serializers.SerializerMethodField()

    class Meta:
        model = Oeuvre
        fields = WorkTitleMixin.TITLE_FIELDS + ('extrait_de',)

    def get_extrait_de(self, obj):
        if obj.extrait_de_id is None:
            return None
        return WorkAncestorSerializer(obj.extrait_de, context=self.context).data


class WorkSerializer(WorkTitleMixin):
    pupitres = PupitreSerializer(many=True)
    auteurs = AuteurSerializer(many=True)
    # "Genèse et création" column of the Django œuvre table.
    creation = serializers.SerializerMethodField()
    # Parent-work chain, so the frontend can prepend ancestor titles like Django.
    extrait_de = serializers.SerializerMethodField()

    class Meta:
        model = Oeuvre
        fields = WorkTitleMixin.TITLE_FIELDS + (
            'extrait_de', 'pupitres', 'auteurs', 'creation',
        )

    def get_creation(self, obj):
        return str(obj.creation) or None

    def get_extrait_de(self, obj):
        if obj.extrait_de_id is None:
            return None
        return WorkAncestorSerializer(obj.extrait_de, context=self.context).data


class DossierWorkSerializer(WorkSerializer):
    """``WorkSerializer`` plus each work's grouped sources.

    Used by the dossier d'œuvres works list, which mirrors the Django
    ``dossier_oeuvres_data_detail`` template: every work carries the same
    grouped sources block shown on its detail page (see
    ``WorkDetailSerializer.get_sources``).
    """
    sources = serializers.SerializerMethodField()

    class Meta(WorkSerializer.Meta):
        fields = WorkSerializer.Meta.fields + ('sources',)

    def get_sources(self, obj):
        return grouped_sources(
            obj.sources.published(request=self.context.get('request'))
            .prefetch(), self.context)


class CaracteristiqueSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = CaracteristiqueDeProgramme
        fields = ('valeur', 'type')

    def get_type(self, obj):
        return {'nom': obj.type.nom} if obj.type_id else None


class DistributionElementSerializer(serializers.ModelSerializer):
    individu = PersonSerializer()
    ensemble = EnsembleSerializer()
    partie = PartSerializer()
    profession = ProfessionSerializer()

    class Meta:
        model = ElementDeDistribution
        fields = ('id', 'individu', 'ensemble', 'partie', 'profession')


class ProgrammeElementSerializer(serializers.ModelSerializer):
    oeuvre = WorkSerializer()
    caracteristiques = CaracteristiqueSerializer(many=True)
    distribution = DistributionElementSerializer(many=True)
    numero = serializers.SerializerMethodField()

    class Meta:
        model = ElementDeProgramme
        fields = ('id', 'numerotation', 'numero', 'oeuvre', 'autre',
                  'caracteristiques', 'distribution')

    def get_numero(self, obj):
        # ``_numero`` is filled in EvenementSerializer.get_programme.
        return getattr(obj, '_numero', '')


def _fill_numeros(elements):
    """Replicate ``ElementDeProgrammeQueryset.fill_numeros`` on a (prefetched) list."""
    sans_ordre = ElementDeProgramme.NUMEROTATIONS_SANS_ORDRE
    numbered = [e for e in elements if e.numerotation not in sans_ordre]
    for element in elements:
        if element.numerotation in sans_ordre:
            element._numero = ''
        else:
            element._numero = len(
                [e for e in numbered if e.position <= element.position])
    return elements


class EvenementSerializer(MetaTypeMixin, serializers.ModelSerializer):
    debut_lieu = PlaceSerializer()
    fin_lieu = PlaceSerializer()
    caracteristiques = CaracteristiqueSerializer(many=True)
    distribution = DistributionElementSerializer(many=True)
    programme = serializers.SerializerMethodField()
    sources = serializers.SerializerMethodField()

    class Meta:
        model = Evenement
        fields = (
            'id', 'meta',
            'debut_date', 'debut_date_approx', 'debut_heure',
            'debut_heure_approx', 'debut_lieu', 'debut_lieu_approx',
            'fin_date', 'fin_date_approx', 'fin_heure', 'fin_heure_approx',
            'fin_lieu', 'fin_lieu_approx',
            'circonstance', 'relache', 'programme_incomplet',
            'recette_generale', 'caracteristiques',
            'distribution', 'programme', 'sources',
        )

    def get_programme(self, obj):
        elements = _fill_numeros(list(obj.programme.all()))
        return ProgrammeElementSerializer(
            elements, many=True, context=self.context).data

    def get_sources(self, obj):
        # The event's published sources, grouped by type. ``obj.sources`` is
        # prefetched (already published, ordered and ``select_related('type')``)
        # by ``EvenementViewSet`` so this adds no per-row query.
        return grouped_sources(obj.sources.all(), self.context)


class EvenementDetailSerializer(AdminLinkMixin, EtatMixin,EvenementSerializer):
    """Event detail adds the public notes and publication state.

    Used only by the ``retrieve`` action so the (paginated) list rows stay lean
    and avoid the extra ``etat`` join per row.
    """
    notes_publiques = serializers.CharField()

    class Meta(EvenementSerializer.Meta):
        fields = (EvenementSerializer.Meta.fields
                  + ('etat', 'notes_publiques') + ADMIN_LINK_FIELDS)


# -- Index/detail serializers for the standalone entity pages ----------------

class PersonDetailSerializer(AdminLinkMixin, EtatMixin,PersonSerializer):
    """``PersonSerializer`` plus the extra fields shown on a person's page."""
    isni = serializers.CharField(allow_blank=True)
    biographie = serializers.CharField(allow_blank=True)
    naissance = serializers.SerializerMethodField()
    deces = serializers.SerializerMethodField()
    professions = ProfessionSerializer(many=True)
    notes_publiques = serializers.CharField()
    # The heavy related collections are no longer inlined: they are fetched a
    # page at a time from ``PublicIndividuViewSet.related``. Only their totals
    # are exposed here, so the frontend can render section headers and drop
    # empty sections without a round-trip.
    oeuvres_count = serializers.SerializerMethodField()
    membre_de = serializers.SerializerMethodField()
    parties_creees_count = serializers.SerializerMethodField()
    publications_count = serializers.SerializerMethodField()
    dedicaces_count = serializers.SerializerMethodField()
    parents = serializers.SerializerMethodField()
    enfants = serializers.SerializerMethodField()
    sources = serializers.SerializerMethodField()

    class Meta(PersonSerializer.Meta):
        fields = PersonSerializer.Meta.fields + (
            'isni', 'biographie', 'naissance', 'deces', 'professions', 'etat',
            'notes_publiques', 'oeuvres_count', 'membre_de',
            'parties_creees_count', 'publications_count', 'dedicaces_count',
            'parents', 'enfants', 'sources',
        ) + ADMIN_LINK_FIELDS

    def _published(self, queryset):
        return queryset.published(request=self.context.get('request'))

    def get_sources(self, obj):
        return grouped_sources(
            self._published(obj.sources).prefetch(), self.context)

    def get_naissance(self, obj):
        return str(obj.naissance)

    def get_deces(self, obj):
        return str(obj.deces)

    def get_oeuvres_count(self, obj):
        return self._published(obj.oeuvres()).count()

    def get_membre_de(self, obj):
        ensembles = [m.ensemble for m in obj.membre_de() if m.ensemble_id]
        return EnsembleSerializer(
            ensembles, many=True, context=self.context).data

    def get_parties_creees_count(self, obj):
        return self._published(obj.parties_creees).count()

    def get_publications_count(self, obj):
        return self._published(obj.publications()).count()

    def get_dedicaces_count(self, obj):
        return self._published(obj.dedicaces).count()

    def get_parents(self, obj):
        parentes = obj.parentes.filter(
            parent__etat__public=True).select_related('type', 'parent')
        return group_parentes(parentes, 'parent', PersonSerializer,
                              self.context)

    def get_enfants(self, obj):
        enfances = obj.enfances.filter(
            enfant__etat__public=True).select_related('type', 'enfant')
        return group_parentes(enfances, 'enfant', PersonSerializer,
                             self.context)


class EnsembleDetailSerializer(AdminLinkMixin, EtatMixin,EnsembleSerializer):
    type = serializers.SerializerMethodField()
    isni = serializers.CharField(allow_blank=True)
    siege = PlaceSerializer()
    smart_period = serializers.SerializerMethodField()
    notes_publiques = serializers.CharField()
    # Heavy related collections: only their totals are inlined; the chips are
    # fetched a page at a time from ``PublicEnsembleViewSet.related`` (see the
    # ``RELATED_COLLECTIONS`` registry there).
    membres_count = serializers.SerializerMethodField()
    oeuvres_count = serializers.SerializerMethodField()
    evenements_par_territoire = serializers.SerializerMethodField()
    sources = serializers.SerializerMethodField()

    class Meta(EnsembleSerializer.Meta):
        fields = EnsembleSerializer.Meta.fields + (
            'type', 'etat', 'isni', 'siege', 'smart_period', 'notes_publiques',
            'membres_count', 'oeuvres_count', 'evenements_par_territoire',
            'sources',
        ) + ADMIN_LINK_FIELDS

    def _published(self, queryset):
        return queryset.published(request=self.context.get('request'))

    def get_type(self, obj):
        return obj.type.nom if obj.type_id else None

    def get_sources(self, obj):
        sources = obj.sources.published(
            request=self.context.get('request')).prefetch()
        return grouped_sources(sources, self.context)

    def get_smart_period(self, obj):
        return str(obj.smart_period()) or None

    def get_membres_count(self, obj):
        return self._published(
            Individu.objects.filter(membres__ensemble=obj).distinct()).count()

    def get_oeuvres_count(self, obj):
        return self._published(obj.oeuvres()).count()

    def get_evenements_par_territoire(self, obj):
        return [
            {'nom': nom, 'count': count, 'exclusive_count': exclusive_count}
            for nom, count, exclusive_count in obj.evenements_par_territoire()
        ]


class PlaceDetailSerializer(AdminLinkMixin, EtatMixin,PlaceSerializer):
    """``PlaceSerializer`` plus the lists shown on a place's page."""
    historique = serializers.CharField()
    notes_publiques = serializers.CharField()
    has_children = serializers.SerializerMethodField()
    # Heavy related collections: only their totals are inlined; the chips are
    # fetched a page at a time from ``PublicLieuViewSet.related``.
    individus_nes_count = serializers.SerializerMethodField()
    individus_decedes_count = serializers.SerializerMethodField()
    oeuvres_creees_count = serializers.SerializerMethodField()
    sources = serializers.SerializerMethodField()

    class Meta(PlaceSerializer.Meta):
        fields = PlaceSerializer.Meta.fields + (
            'etat', 'historique', 'notes_publiques', 'has_children',
            'individus_nes_count', 'individus_decedes_count',
            'oeuvres_creees_count', 'sources',
        ) + ADMIN_LINK_FIELDS

    def _published(self, queryset):
        return queryset.published(request=self.context.get('request'))

    def get_has_children(self, obj):
        return self._published(obj.get_children()).exists()

    def get_sources(self, obj):
        return grouped_sources(
            self._published(obj.sources).prefetch(), self.context)

    def get_individus_nes_count(self, obj):
        return self._published(obj.individus_nes()).count()

    def get_individus_decedes_count(self, obj):
        return self._published(obj.individus_decedes()).count()

    def get_oeuvres_creees_count(self, obj):
        return self._published(obj.oeuvres_creees()).count()


class ProfessionDetailSerializer(AdminLinkMixin, EtatMixin,ProfessionSerializer):
    """``ProfessionSerializer`` plus the lists shown on a profession's page."""
    # Heavy related collections: only their totals are inlined; the chips are
    # fetched a page at a time from ``PublicProfessionViewSet.related``.
    parties_count = serializers.SerializerMethodField()
    individus_count = serializers.SerializerMethodField()
    oeuvres_count = serializers.SerializerMethodField()
    sources = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()

    class Meta(ProfessionSerializer.Meta):
        fields = ProfessionSerializer.Meta.fields + (
            'etat', 'parties_count', 'individus_count', 'oeuvres_count',
            'sources', 'parent', 'has_children',
        ) + ADMIN_LINK_FIELDS

    def _published(self, queryset):
        return queryset.published(request=self.context.get('request'))

    def get_parties_count(self, obj):
        return self._published(obj.parties.all()).count()

    def get_individus_count(self, obj):
        return self._published(obj.individus).count()

    def get_oeuvres_count(self, obj):
        return self._published(obj.auteurs.oeuvres()).count()

    def get_sources(self, obj):
        return SourceSerializer(
            self._published(obj.auteurs.sources()), many=True,
            context=self.context).data

    def get_parent(self, obj):
        if obj.parent_id is None:
            return None
        return ProfessionSerializer(obj.parent, context=self.context).data

    def get_has_children(self, obj):
        return self._published(obj.get_children()).exists()


class PartDetailSerializer(AdminLinkMixin, EtatMixin,PartSerializer):
    """``PartSerializer`` plus the lists shown on a rôle/instrument page."""
    # Unlike the chip serializer, the detail page does show the linked work.
    oeuvre = WorkSerializer()
    professions = serializers.SerializerMethodField()
    premier_interprete = serializers.SerializerMethodField()
    premier_interprete_feminin = serializers.SerializerMethodField()
    # Heavy related collections: only their totals are inlined; the chips are
    # fetched a page at a time from ``PublicPartieViewSet.related``.
    interpretes_count = serializers.SerializerMethodField()
    repertoire_count = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()
    notes_publiques = serializers.CharField()
    sources = serializers.SerializerMethodField()

    class Meta(PartSerializer.Meta):
        fields = PartSerializer.Meta.fields + (
            'etat', 'professions', 'premier_interprete',
            'premier_interprete_feminin', 'interpretes_count',
            'repertoire_count', 'parent', 'has_children', 'notes_publiques',
            'sources',
        ) + ADMIN_LINK_FIELDS

    def _published(self, queryset):
        return queryset.published(request=self.context.get('request'))

    def get_sources(self, obj):
        return grouped_sources(
            self._published(obj.sources).prefetch(), self.context)

    def get_professions(self, obj):
        return ProfessionSerializer(
            obj.professions.all(), many=True, context=self.context).data

    def get_premier_interprete(self, obj):
        if obj.premier_interprete_id is None:
            return None
        return PersonSerializer(
            obj.premier_interprete, context=self.context).data

    def get_premier_interprete_feminin(self, obj):
        return bool(obj.premier_interprete_id
                    and obj.premier_interprete.is_feminin())

    def get_interpretes_count(self, obj):
        return self._published(obj.interpretes()).count()

    def get_repertoire_count(self, obj):
        return self._published(obj.repertoire()).count()

    def get_parent(self, obj):
        if obj.parent_id is None:
            return None
        return PartSerializer(obj.parent, context=self.context).data

    def get_has_children(self, obj):
        return self._published(obj.get_children()).exists()


class WorkDetailSerializer(AdminLinkMixin, EtatMixin,WorkSerializer):
    """``WorkSerializer`` plus the relations shown on an œuvre's page."""
    # Raw ambitus endpoints (note index + octave); the frontend localises the
    # note names itself, like it does for the tonalité.
    ambitus = serializers.SerializerMethodField()
    notes_publiques = serializers.CharField()
    has_children = serializers.SerializerMethodField()
    # Heavy related collection: only its total is inlined; the chips are fetched
    # a page at a time from ``PublicOeuvreViewSet.related``.
    dedicataires_count = serializers.SerializerMethodField()
    parents = serializers.SerializerMethodField()
    enfants = serializers.SerializerMethodField()
    oeuvres_associees = serializers.SerializerMethodField()
    sources = serializers.SerializerMethodField()

    class Meta(WorkSerializer.Meta):
        fields = WorkSerializer.Meta.fields + (
            'etat', 'ambitus', 'notes_publiques', 'has_children',
            'dedicataires_count', 'parents', 'enfants', 'oeuvres_associees',
            'sources',
        ) + ADMIN_LINK_FIELDS

    def _published(self, queryset):
        return queryset.published(request=self.context.get('request'))

    def get_sources(self, obj):
        return grouped_sources(
            self._published(obj.sources).prefetch(), self.context)

    def get_ambitus(self, obj):
        return obj.ambitus_pitches()

    def get_has_children(self, obj):
        return self._published(obj.get_children()).exists()

    def get_dedicataires_count(self, obj):
        return self._published(obj.dedicataires).count()

    def get_parents(self, obj):
        # Mother works, grouped by parenté type (the "Mères en ordre" block).
        parentes = obj.parentes_meres.meres_en_ordre().filter(
            mere__etat__public=True).select_related('type', 'mere')
        return group_parentes(parentes, 'mere', WorkSerializer, self.context)

    def get_enfants(self, obj):
        # Daughter works, grouped by parenté type (the "Filles en ordre" block).
        parentes = obj.parentes_filles.filles_en_ordre().filter(
            fille__etat__public=True).select_related('type', 'fille')
        return group_parentes(parentes, 'fille', WorkSerializer, self.context)

    def get_oeuvres_associees(self, obj):
        # Authenticated-only, mirroring the Django template's `{% if user… %}`.
        request = self.context.get('request')
        if request is None or not request.user.is_authenticated:
            return []
        return WorkSerializer(
            self._published(obj.oeuvres_associees()), many=True,
            context=self.context).data


class SourceSerializer(MetaTypeMixin, serializers.ModelSerializer):
    """Lightweight source card/detail (title + type), for the source index."""
    title = serializers.CharField(source='__str__')
    type = serializers.SerializerMethodField()

    class Meta:
        model = Source
        fields = ('id', 'meta', 'title', 'type')

    def get_type(self, obj):
        return obj.type.nom if obj.type_id else None


class SourceDetailSerializer(AdminLinkMixin, EtatMixin,SourceSerializer):
    """Full source page: the three Django tabs (présentation, consulter, index)."""
    pretty_title = serializers.SerializerMethodField()
    legende = serializers.CharField()
    notes_publiques = serializers.CharField()
    has_presentation_tab = serializers.SerializerMethodField()
    has_index_tab = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    auteurs_html = serializers.SerializerMethodField()
    # Index tab.
    nested_individus = serializers.SerializerMethodField()
    nested_oeuvres = serializers.SerializerMethodField()
    nested_parties = serializers.SerializerMethodField()
    nested_lieux = serializers.SerializerMethodField()
    nested_ensembles = serializers.SerializerMethodField()
    # Consulter tab.
    is_audio = serializers.BooleanField()
    is_video = serializers.BooleanField()
    is_collection = serializers.BooleanField()
    is_image = serializers.BooleanField()
    media = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    collection_children = serializers.SerializerMethodField()
    # The transcribed text and the download/external-link button shown alongside
    # the media in the Consulter tab (mirrors the legacy ``SourceView``).
    transcription = serializers.CharField()
    download = serializers.SerializerMethodField()
    # Présentation tab.
    presentation = serializers.CharField()
    contexte = serializers.CharField()
    sources_et_protocole = serializers.CharField()
    bibliographie = serializers.CharField()
    # Présentation-tab sidebar (mirrors the Django ``sidebar_base.html``).
    publications = serializers.CharField()
    developpements = serializers.CharField()
    citation = serializers.SerializerMethodField()

    class Meta(SourceSerializer.Meta):
        fields = SourceSerializer.Meta.fields + (
            'etat', 'pretty_title', 'legende', 'notes_publiques',
            'has_presentation_tab', 'has_index_tab', 'parent', 'auteurs_html',
            'nested_individus', 'nested_oeuvres', 'nested_parties',
            'nested_lieux', 'nested_ensembles',
            'is_audio', 'is_video', 'is_collection', 'is_image',
            'media', 'images', 'collection_children',
            'transcription', 'download',
            'presentation', 'contexte', 'sources_et_protocole',
            'bibliographie', 'publications', 'developpements', 'citation',
        ) + ADMIN_LINK_FIELDS

    def _published(self, queryset):
        return queryset.published(request=self.context.get('request'))

    def get_pretty_title(self, obj):
        return obj.pretty_title()

    def get_has_presentation_tab(self, obj):
        return obj.has_presentation_tab()

    def get_has_index_tab(self, obj):
        return obj.has_index_tab()

    def get_parent(self, obj):
        if obj.parent_id is None:
            return None
        return SourceSerializer(obj.parent, context=self.context).data

    def get_auteurs_html(self, obj):
        return obj.auteurs_html() or None

    def get_nested_individus(self, obj):
        return PersonSerializer(
            self._published(obj.nested_individus()), many=True,
            context=self.context).data

    def get_nested_oeuvres(self, obj):
        return WorkSerializer(
            self._published(obj.nested_oeuvres()), many=True,
            context=self.context).data

    def get_nested_parties(self, obj):
        return PartSerializer(
            obj.nested_parties(), many=True, context=self.context).data

    def get_nested_lieux(self, obj):
        return PlaceSerializer(
            self._published(obj.nested_lieux()), many=True,
            context=self.context).data

    def get_nested_ensembles(self, obj):
        return EnsembleSerializer(
            self._published(obj.nested_ensembles()), many=True,
            context=self.context).data

    def get_media(self, obj):
        if not (obj.is_audio() or obj.is_video()):
            return None
        specific = obj.specific
        request = self.context.get('request')
        authenticated = bool(request and request.user.is_authenticated)
        has_excerpt = bool(specific.extrait_ogg or specific.extrait_mpeg)
        # Same gate as ``source_content.html``: full file for logged-in users or
        # when there is no excerpt; otherwise the excerpt.
        full = authenticated or not has_excerpt
        kind = 'audio' if obj.is_audio() else 'video'
        ogg = specific.fichier_ogg if full else specific.extrait_ogg
        mpeg = specific.fichier_mpeg if full else specific.extrait_mpeg
        sources = []
        if ogg:
            sources.append({'url': ogg.url, 'mimetype': f'{kind}/ogg'})
        if mpeg:
            mime = 'audio/mpeg' if kind == 'audio' else 'video/mp4'
            sources.append({'url': mpeg.url, 'mimetype': mime})
        media = {'kind': kind, 'is_full': full, 'sources': sources}
        if kind == 'video':
            media['width'] = (specific.largeur if full
                              else specific.largeur_extrait)
            media['height'] = (specific.hauteur if full
                               else specific.hauteur_extrait)
        return media

    def _image_related(self, image):
        # The catalogue entities linked to a single page, shown as chips in the
        # image reader (mirrors the old ``Reader``'s per-page ``Related`` row).
        # Same chip set as the Index tab's ``nested_*`` but scoped to this one
        # image; events are omitted because the frontend ``EntityChip`` has no
        # event chip. Published filtering matches ``get_nested_*``.
        related = []
        related += PersonSerializer(
            self._published(image.linked_individus), many=True,
            context=self.context).data
        related += WorkSerializer(
            self._published(image.linked_oeuvres), many=True,
            context=self.context).data
        related += PartSerializer(
            image.linked_parties, many=True, context=self.context).data
        related += PlaceSerializer(
            self._published(image.linked_lieux), many=True,
            context=self.context).data
        related += EnsembleSerializer(
            self._published(image.linked_ensembles), many=True,
            context=self.context).data
        return related

    def get_images(self, obj):
        if not obj.has_images():
            return []
        result = []
        for image in obj.images:
            if not image.fichier:
                continue
            result.append({
                'id': image.pk,
                'label': image.page or image.folio or '',
                'url': image.fichier.url,
                'thumbnail': image.medium_thumbnail,
                'related': self._image_related(image),
                # Per-page owner + admin links, like the old reader's per-page
                # ``ModelToolbar`` (each page is its own ``Source``).
                'admin': admin_link_data(image, self.context.get('request')),
            })
        return result

    def get_collection_children(self, obj):
        if not obj.is_collection:
            return []
        children = self._published(obj.children).select_related('type')
        return SourceSerializer(
            children, many=True, context=self.context).data

    def get_download(self, obj):
        # Mirrors the legacy ``SourceView`` download button: an external
        # permalink ('link') or, for an 'autre'-type source, the downloadable
        # file ('file') with its human-readable size. Gated on
        # ``telechargement_autorise``.
        if not obj.telechargement_autorise:
            return None
        if obj.url:
            return {'kind': 'link', 'url': obj.url}
        if obj.is_other() and obj.fichier:
            try:
                size = obj.fichier.size
            except (ValueError, FileNotFoundError):
                size = 0
            return {'kind': 'file', 'url': obj.fichier.url,
                    'size': filesizeformat(size)}
        return None

    def get_citation(self, obj):
        if not obj.has_presentation_tab():
            return None
        return {
            'title': str(obj),
            # Relative path; the frontend prefixes the canonical dezede.org
            # domain (see ``CitationReference``), matching the letter citation.
            'url': obj.get_absolute_url(),
            'editeurs': [str(u) for u in obj.editeurs_scientifiques.all()],
            'date_publication': (obj.date_publication.isoformat()
                                 if obj.date_publication else None),
        }


# -- Row serializers for the MUI X data grids --------------------------------
# These add exactly the extra columns the matching Django ``*TableView`` shows,
# on top of the existing chip serializers (so the React chip formatters keep
# rendering the primary label unchanged).

class PersonRowSerializer(PersonSerializer):
    """Person chip + the profession/birth/death columns of the individu table."""
    professions = ProfessionSerializer(many=True)
    naissance = serializers.SerializerMethodField()
    deces = serializers.SerializerMethodField()

    class Meta(PersonSerializer.Meta):
        fields = PersonSerializer.Meta.fields + (
            'professions', 'naissance', 'deces',
        )

    def get_naissance(self, obj):
        return str(obj.naissance) or None

    def get_deces(self, obj):
        return str(obj.deces) or None


class EnsembleRowSerializer(EnsembleSerializer):
    """Ensemble chip + the type/siège columns of the ensemble table."""
    type = serializers.SerializerMethodField()
    siege = serializers.SerializerMethodField()

    class Meta(EnsembleSerializer.Meta):
        fields = EnsembleSerializer.Meta.fields + ('type', 'siege')

    def get_type(self, obj):
        return obj.type.nom if obj.type_id else None

    def get_siege(self, obj):
        return obj.siege.nom if obj.siege_id else None


class PartRowSerializer(PartSerializer):
    """Part chip + the human-readable type (instrument/rôle) column."""
    type_display = serializers.CharField(source='get_type_display')

    class Meta(PartSerializer.Meta):
        fields = PartSerializer.Meta.fields + ('type_display',)


class ProfessionRowSerializer(ProfessionSerializer):
    """Profession chip + the individus/œuvres count columns (annotated)."""
    individus_count = serializers.IntegerField(read_only=True)
    oeuvres_count = serializers.IntegerField(read_only=True)

    class Meta(ProfessionSerializer.Meta):
        fields = ProfessionSerializer.Meta.fields + (
            'individus_count', 'oeuvres_count',
        )


class SourceRowSerializer(SourceSerializer):
    """Source chip + the date and content-type (icons) columns."""
    ancrage = serializers.SerializerMethodField()
    data_types = serializers.ReadOnlyField()

    class Meta(SourceSerializer.Meta):
        fields = SourceSerializer.Meta.fields + ('ancrage', 'data_types')

    def get_ancrage(self, obj):
        return str(obj.ancrage) or None


class SourceGallerySerializer(SourceSerializer):
    """A promoted source as it appears in the bibliothèque gallery.

    Mirrors the legacy ``bibliotheque_source.html`` card: the title plus either a
    preview-image thumbnail or, failing that, a short transcription excerpt (the
    frontend shows a "no preview" placeholder when both are empty). ``data_types``
    drives the content-type icons, like the index row serializer.
    """
    thumbnail = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    data_types = serializers.ReadOnlyField()
    # ``_pages_count`` is annotated by ``PublicSourceViewSet.bibliotheque``; the
    # frontend badges tiles with more than one page as multi-page books.
    pages_count = serializers.IntegerField(source='_pages_count', default=0)

    class Meta(SourceSerializer.Meta):
        fields = SourceSerializer.Meta.fields + (
            'thumbnail', 'excerpt', 'data_types', 'pages_count')

    def get_thumbnail(self, obj):
        image = obj.preview_image
        if image is None:
            return None
        thumbnail = image.medium_thumbnail_object
        if thumbnail is None:
            return None
        # The intrinsic size lets the frontend balance the masonry columns
        # deterministically (and reserve the tile's space before the image
        # loads), so tiles never reshuffle and columns stay even in height.
        return {
            'src': thumbnail.url,
            'width': thumbnail.width,
            'height': thumbnail.height,
        }

    def get_excerpt(self, obj):
        # Only needed as a fallback when there is no preview image, matching the
        # ``{% elif source.transcription %}`` branch of the legacy template.
        if obj.preview_image is not None or not obj.transcription:
            return None
        return Truncator(obj.transcription_text).words(36) or None
