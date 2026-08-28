import json

from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _, get_language
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.contrib.sites.models import Site
from wagtail.search.backends import get_search_backend

from accounts.models import HierarchicUser
from accounts.serializers import UserSerializer
from common.utils.export import is_user_locked, lock_user
from ...jobs import events_to_csv, events_to_xlsx, events_to_json
from ...models import *
from ...templatetags.extras import get_data
from ...views import PublishedMixin, DEFAULT_MIN_PLACES, MAX_MIN_PLACES
from .filters import (
    EvenementFilterBackend, filter_evenements_queryset, evenement_facets,
)
from .serializers import (
    IndividuSerializer, EnsembleSerializer, LieuSerializer, OeuvreSerializer,
    SourceSerializer, EvenementSerializer, PartieSerializer,
    AuteurSerializer, ProfessionSerializer,
)
from . import public_serializers


class IndividuViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Individu
    queryset = model.objects.prefetch_related('professions', 'parents')
    serializer_class = IndividuSerializer


class EnsembleViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Ensemble
    queryset = model.objects.select_related('type')
    serializer_class = EnsembleSerializer


class LieuViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Lieu
    queryset = model.objects.select_related('parent__nature', 'nature')
    serializer_class = LieuSerializer


class OeuvreViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Oeuvre
    queryset = model.objects.prefetch_related('extrait_de',
                                              'auteurs__profession')
    serializer_class = OeuvreSerializer


class SourceViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Source
    queryset = Source.objects.prefetch_related(
        'evenements', 'oeuvres', 'individus', 'ensembles', 'lieux', 'parties',
        'editeurs_scientifiques', 'auteurs',
    )
    serializer_class = SourceSerializer


class AuteurViewSet(ReadOnlyModelViewSet):
    model = Auteur
    queryset = Auteur.objects.all()
    serializer_class = AuteurSerializer


class ProfessionViewSet(ReadOnlyModelViewSet):
    model = Profession
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer


# Eager-loading for the public, nested event serialization (list & detail).
EVENEMENT_PUBLIC_SELECT = (
    'debut_lieu__nature', 'debut_lieu__parent',
    'fin_lieu__nature', 'fin_lieu__parent',
)
EVENEMENT_PUBLIC_PREFETCH = (
    'caracteristiques__type',
    'distribution__individu', 'distribution__ensemble',
    'distribution__partie', 'distribution__profession',
    'programme__caracteristiques__type',
    'programme__oeuvre__genre',
    'programme__oeuvre__auteurs__individu',
    'programme__oeuvre__auteurs__ensemble',
    'programme__oeuvre__auteurs__profession',
    'programme__oeuvre__pupitres__partie',
    'programme__distribution__individu',
    'programme__distribution__ensemble',
    'programme__distribution__partie',
    'programme__distribution__profession',
)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Session auth without CSRF enforcement for the event export POST action.
    The export only enqueues a job emailed to the requesting user, so the SPA
    can POST with just the session cookie rather than plumbing a CSRF token."""

    def enforce_csrf(self, request):
        return


class EvenementViewSet(PublishedMixin, ReadOnlyModelViewSet):
    """Public, read-only event API for the Next.js frontend.

    Supports the same filters as the HTML list view (see
    :mod:`libretto.api.rest.filters`), ``?limit=&offset=`` pagination (infinite
    scroll), and the ``facets``/``geojson`` actions plus per-entity
    autocomplete actions used by the filter form.
    """
    authentication_classes = [CsrfExemptSessionAuthentication]
    model = Evenement
    queryset = Evenement.objects.all()
    serializer_class = public_serializers.EvenementSerializer
    filter_backends = (EvenementFilterBackend,)
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        # The detail endpoint adds the public notes + état and the owner + admin
        # links (object-level); the list endpoint omits them so it does not pay a
        # per-row owner lookup / permission check.
        if self.action == 'retrieve':
            return public_serializers.EvenementDetailSerializer
        return super().get_serializer_class()

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)
        # Each event's published sources (grouped by type in the serializer) are
        # shown on every card — list and detail. Prefetch them in one query,
        # ``SourceQuerySet.prefetch()`` covering ``str(source)`` →
        # ``Source.html()`` plus the ``has_children_images`` annotation that
        # keeps ``data_types`` query-free.
        return qs.select_related(*EVENEMENT_PUBLIC_SELECT) \
                 .prefetch_related(
                     *EVENEMENT_PUBLIC_PREFETCH,
                     Prefetch('sources',
                              queryset=Source.objects.published(self.request)
                                       .prefetch()),
                 )

    @action(detail=False)
    def facets(self, request):
        return Response(evenement_facets(
            self.get_queryset(), request.query_params,
            request.user.is_authenticated))

    @action(detail=False)
    def yearly_counts(self, request):
        # Per-year event counts for the current filters, mirroring the HTML
        # autorité detail listing (``EvenementQuerySet.yearly_counts`` /
        # ``routines/evenement_list_def.html``). ``year`` is the civil year as an
        # int; the rows are ordered oldest-first.
        qs = filter_evenements_queryset(self.get_queryset(),
                                        request.query_params)
        return Response([
            {'year': row['year'].year, 'count': row['count']}
            for row in qs.yearly_counts()
        ])

    @action(detail=False)
    def geojson(self, request):
        qs = filter_evenements_queryset(self.get_queryset(),
                                        request.query_params)
        bbox = request.query_params.get('bbox')
        if bbox:
            bbox = Polygon.from_bbox([float(c) for c in bbox.split(',')])
        else:
            bbox = None
        min_places = request.query_params.get('min_places',
                                              str(DEFAULT_MIN_PLACES))
        min_places = (int(min_places) if min_places.isdigit()
                      else DEFAULT_MIN_PLACES)
        min_places = min(min_places, MAX_MIN_PLACES)
        features = []
        for pk, nom, geometry, n in get_data(qs, min_places, bbox):
            # ``get_data`` returns whatever geometry the aggregated ancestor
            # place stores (a Point for a city, but a Polygon/MultiPolygon for a
            # region or country). The map renders dots, so we always emit the
            # centroid as a Point — otherwise non-Point geometries have no
            # ``coordinates[0]/[1]`` and the marker silently disappears.
            point = GEOSGeometry(geometry).point_on_surface
            features.append({
                'type': 'Feature',
                'properties': {'lieu_pk': pk, 'tooltip': f'{nom} ({n})', 'n': n},
                'geometry': json.loads(point.json),
            })
        return Response({'type': 'FeatureCollection', 'features': features})

    # -- Filter-form autocompletes (TRelated* shapes) ----------------------

    def _autocomplete(self, request, model, serializer_class, prefetch=()):
        qs = model.objects.all().published(request=request)
        if prefetch:
            qs = qs.prefetch_related(*prefetch)
        # ``ids`` resolves a selection (pipe- or comma-separated pks) back to
        # objects so the filter form can label items restored from the URL.
        ids = request.query_params.get('ids')
        if ids:
            pk_list = [pk for pk in ids.replace('|', ',').split(',')
                       if pk.isdigit()]
            qs = qs.filter(pk__in=pk_list)
            return Response(serializer_class(
                qs, many=True, context={'request': request}).data)
        q = request.query_params.get('q', '').strip()
        if q:
            # Prefix type-ahead (``autocomplete()``), not full-text ``search()``:
            # the filter form's boxes match as the user types each word.
            qs = get_search_backend().autocomplete(q, qs).get_queryset()
        qs = qs[:20]
        return Response(
            serializer_class(qs, many=True, context={'request': request}).data)

    @action(detail=False)
    def lieux(self, request):
        return self._autocomplete(
            request, Lieu, public_serializers.PlaceSerializer)

    @action(detail=False)
    def individus(self, request):
        return self._autocomplete(
            request, Individu, public_serializers.PersonSerializer)

    @action(detail=False)
    def ensembles(self, request):
        return self._autocomplete(
            request, Ensemble, public_serializers.EnsembleSerializer)

    @action(detail=False)
    def oeuvres(self, request):
        return self._autocomplete(
            request, Oeuvre, public_serializers.WorkSerializer,
            prefetch=('genre', 'pupitres__partie', 'auteurs__individu',
                      'auteurs__ensemble', 'auteurs__profession'))

    @action(detail=False, methods=['post'])
    def export(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'code': 'export_not_authenticated',
                 'detail': _('Vous devez être connecté pour lancer un export.')},
                status=403)
        if is_user_locked(request.user):
            return Response(
                {'code': 'export_in_progress',
                 'detail': _('Un export de votre part est déjà en cours. '
                             'Veuillez attendre la fin de celui-ci avant d’en '
                             'lancer un autre.')},
                status=409)
        fmt = (request.data.get('format') or '').lower()
        jobs = {'csv': events_to_csv, 'xlsx': events_to_xlsx,
                'json': events_to_json}
        if fmt not in jobs:
            return Response({'detail': 'Invalid format.'}, status=400)
        qs = filter_evenements_queryset(self.get_queryset(), request.query_params)
        pk_list = list(qs.values_list('pk', flat=True))
        lock_user(request.user)
        site = Site.objects.get_current(request)
        language_code = getattr(request, 'LANGUAGE_CODE', None) or get_language()
        jobs[fmt].delay(pk_list, request.user.pk, site.pk, language_code)
        return Response(
            {'code': 'export_started',
             'format': fmt.upper(),
             'detail': _('La génération de l’export %s est en cours. Un '
                         'courriel le contenant vous sera envoyé d’ici quelques '
                         'minutes.') % fmt.upper()},
            status=202)


class PartieViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Partie
    queryset = Partie.objects.all()
    serializer_class = PartieSerializer


class UserViewSet(ReadOnlyModelViewSet):
    model = HierarchicUser
    queryset = HierarchicUser.objects.all()
    serializer_class = UserSerializer
