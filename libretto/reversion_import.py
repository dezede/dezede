"""
Turns the old django-reversion history into Wagtail revisions.

One reversion revision that holds a version of an authority object becomes one
Wagtail ``Revision`` of that object, with its child rows, plus a
``ModelLogEntry`` so that it shows in the History screen. A snapshot is only
read, never saved through the models.

The old admin did not store every child row in every revision (see ``Rel``),
so the rows of a revision are rebuilt from the versions around its date.
Wagtail takes the newest revision as the current state, so after an object's
history is imported, its newest revision is checked against the live object.
"""
import datetime
import json
import re
from collections import Counter, defaultdict
from contextlib import nullcontext

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import GEOSGeometry
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection
from django.utils import timezone
from django.utils.encoding import is_protected_type
from wagtail.models import ModelLogEntry, Revision

DOUBTFUL_MESSAGE = (
    'Cette version vient de l’ancien historique et elle est incomplète ou '
    'douteuse (%s). On peut la consulter et la comparer, mais pas la '
    'restaurer.'
)

REASON_LABELS = {
    'lost': 'données perdues',
    'deleted_unknown': 'lignes supprimées à une date inconnue',
    'unknown_row': 'lignes liées introuvables',
    'child_unreadable': 'lignes liées illisibles',
}


def reason_label(reason):
    return REASON_LABELS.get(reason.split(':')[0], reason)


def doubtful_entry(revision_id):
    """The log entry that marks an imported revision as doubtful, if any."""
    return ModelLogEntry.objects.filter(
        revision_id=revision_id, data__doubtful=True).first()


def doubtful_message(entry):
    reasons = {reason_label(r) for r in entry.data.get('doubtful_reasons', [])}
    return DOUBTFUL_MESSAGE % ', '.join(sorted(reasons))


ACTION_EDIT = 'libretto.reversion.edit'
ACTION_CREATE = 'libretto.reversion.create'
ACTION_TODAY = 'libretto.reversion.today'



INITIAL_COMMENTS = {'initial version', 'version initiale'}


def is_initial(comment):
    """reversion's comment for the first version it made of an object."""
    return (comment or '').strip().rstrip('.').lower() in INITIAL_COMMENTS


def readable_comment(comment, limit=160):
    """
    Django wrote change messages as JSON, such as ``[{"added": {}}]``. They
    become a short French text. Object names in the old texts say nothing.
    """
    comment = (comment or '').strip()
    if is_initial(comment):
        return 'Version initiale'
    if comment.startswith('['):
        try:
            changes = json.loads(comment)
        except ValueError:
            changes = None
        if isinstance(changes, list):
            comment = '. '.join(_change_text(c) for c in changes)
            comment = comment or 'Aucun champ modifié'
    comment = re.sub(r' « \w+ object(?: \(\d+\))? »', '', comment)
    # Django's text for a change with no field name: « de  pour l’objet X ».
    comment = re.sub(r'\bde\s+pour l’objet\s+', 'de ', comment)
    comment = elide(comment).rstrip('.')
    if len(comment) > limit:
        comment = comment[:limit].rstrip() + '…'
    return comment


_ELIDES = re.compile(r'\b([Dd])e (?=[aeiouyhàâäéèêëîïôöùûüœæ])', re.IGNORECASE)


def elide(text):
    """« de élément » becomes « d’élément », outside the quoted names."""
    parts = re.split(r'(«[^»]*»)', text)
    for i in range(0, len(parts), 2):
        parts[i] = _ELIDES.sub(r'\1’', parts[i])
    return ''.join(parts)


def _change_text(change):
    texts = []
    for kind, label in (
            ('added', 'Ajout'), ('changed', 'Modification'),
            ('deleted', 'Suppression')):
        detail = change.get(kind) if isinstance(change, dict) else None
        if detail is None:
            continue
        name = detail.get('name', '')
        fields = ', '.join(f.replace('_', ' ') for f in detail.get('fields', []))
        text = label + (' de %s' % name if name else '')
        texts.append(text + (' (%s)' % fields if fields else ''))
    return ' ; '.join(texts)


# --- Field mapping --------------------------------------------------------
#
# Scalar fields of an old snapshot, by model. Everything else that is not a
# current field is dropped. Keys that are neither mapped nor listed in DROPPED
# are counted, so that a new generation of snapshots does not go unnoticed.
#
# | old key (model)                    | today                              |
# |------------------------------------|------------------------------------|
# | notes (all authority models)       | notes_publiques                    |
# | nom (Source)                       | titre                              |
# | contenu (Source)                   | transcription                      |
# | contenu_dans (Oeuvre)              | extrait_de                         |
# | parente (Partie, Profession)       | parent                             |
# | point (Lieu)                       | geometry                           |
# | ancrage_* (Evenement, Individu,    | lost: the anchor table is gone, so |
# |   Oeuvre)                          | the dates and places are empty and |
# |                                    | the revision is doubtful           |
# | caracteristiques (Evenement,       | child rows, see RELS               |
# |   ElementDeProgramme)              |                                    |
# | professions (Individu, Partie)     | child rows, see RELS               |
# | dedicataire(s) (Oeuvre)            | child rows (Dedicace)              |
# | evenements (Source)                | child rows (SourceEvenement)       |
# | editeurs_scientifiques (Source)    | child rows (SourceUser)            |
# | individus, ensembles, pupitre      | one ElementDeDistribution row per  |
# |   (ElementDeDistribution)          | person or ensemble, partie of the  |
# |                                    | old pupitre                        |
# | content_type, object_id (Auteur,   | the oeuvre or source foreign key   |
# |   ElementDeDistribution)           |                                    |
RENAMES = {
    'evenement': {'notes': 'notes_publiques'},
    'individu': {'notes': 'notes_publiques'},
    'oeuvre': {'notes': 'notes_publiques', 'contenu_dans': 'extrait_de'},
    'partie': {'notes': 'notes_publiques', 'parente': 'parent'},
    'profession': {'notes': 'notes_publiques', 'parente': 'parent'},
    'source': {'notes': 'notes_publiques', 'nom': 'titre',
               'contenu': 'transcription'},
    'lieu': {'notes': 'notes_publiques', 'point': 'geometry'},
    'ensemble': {'notes': 'notes_publiques'},
}
RENAMES['audio'] = RENAMES['video'] = RENAMES['source']

# Anchor ids point to a table that no longer exists.
LOST_KEYS = {
    'evenement': ('ancrage_debut', 'ancrage_fin'),
    'individu': ('ancrage_naissance', 'ancrage_deces'),
    'oeuvre': ('ancrage_creation',),
}

DROPPED = {
    'search_vector', 'autocomplete_vector', 'documents', 'illustrations',
    'personnels', 'level', 'lft', 'rght', 'tree_id', 'polymorphic_ctype',
    'path', 'lilypond', 'description', 'code_programme', 'exoneres',
    'frequentation', 'jauge', 'payantes', 'scolaires', 'code_postal',
    'type_de_scene', 'caracteristiques', 'ancrage_approx', 'documents',
    'latest_revision', 'professions', 'dedicataire', 'dedicataires',
    'evenements', 'editeurs_scientifiques', 'distribution', 'pupitres',
    'parentes', 'content_type', 'object_id', 'individus', 'ensembles',
    'pupitre', 'individus_cibles',
    'ancrage_debut', 'ancrage_fin', 'ancrage_naissance', 'ancrage_deces',
    'ancrage_creation',
}


D = datetime.date


class Rel:
    """
    A child relation of a model, and where its rows come from.

    The old admin did not follow every relation, so the way to rebuild the
    rows depends on the date of the revision. ``modes`` lists
    ``(until, mode)`` pairs, the first one whose date is later than the
    revision wins:

    - followed: the rows are versions in the same reversion revision, the
      state after the save. An empty list is a real state.
    - ids: the parent lists the row ids. The rows were saved on their own
      page, so each one comes from its latest version at that date, in any
      revision.
    - nested: not followed. A revision only holds the rows added or changed
      in that save, so a row belongs to a revision if it had a version by
      then. Deletions were never recorded.
    - list: link rows without versions, listed on the parent.
    """

    def __init__(
            self, name, model, fk, *, modes, gfk=None, ids_key=None,
            list_keys=(), other=None, nested=(), expand=None):
        self.name = name
        self.path = name
        self.model = model          # lower case model name of the rows
        self.fk = fk                # foreign key to the parent on the rows
        self.modes = modes
        self.gfk = gfk              # parent model of old generic rows
        self.ids_key = ids_key      # parent key listing the row ids
        self.list_keys = list_keys  # parent keys listing the other side
        self.other = other          # the other side on a synthesized row
        self.nested = nested
        self.expand = expand
        for child in nested:
            child.path = '%s.%s' % (name, child.name)

    def mode(self, when):
        for until, mode in self.modes:
            if until is None or when < until:
                return mode


FOLLOWED = ((None, 'followed'),)
LIST = ((None, 'list'),)

DISTRIBUTION_OF_PROGRAMME = Rel(
    'distribution', 'elementdedistribution', 'element_de_programme',
    gfk='elementdeprogramme', ids_key='distribution', expand='distribution',
    modes=((D(2015, 5, 13), 'ids'), (None, 'nested')))
SOURCE_LINK = ((D(2014, 11, 10), 'list'), (None, 'followed'))
RELS = {
    'evenement': (
        Rel('programme', 'elementdeprogramme', 'evenement', ids_key='programme',
            modes=((D(2012, 10, 7), 'ids'), (None, 'followed')),
            nested=(
                DISTRIBUTION_OF_PROGRAMME,
                Rel('caracteristiquedeprogrammeelementdeprogramme_set',
                    'caracteristiquedeprogrammeelementdeprogramme', 'element',
                    list_keys=('caracteristiques',), other='caracteristique',
                    modes=LIST),
            )),
        Rel('distribution', 'elementdedistribution', 'evenement',
            gfk='evenement', ids_key='distribution', expand='distribution',
            modes=((D(2013, 1, 15), 'ids'), (None, 'followed'))),
        Rel('caracteristiquedeprogramme_evenements',
            'caracteristiquedeprogrammeevenement', 'evenement',
            list_keys=('caracteristiques',), other='caracteristique',
            modes=LIST),
    ),
    'individu': (
        Rel('parentes', 'parentedindividus', 'enfant', ids_key='parentes',
            modes=((D(2013, 2, 8), 'ids'), (None, 'followed'))),
        Rel('occupations', 'occupation', 'individu',
            list_keys=('professions',), other='profession', modes=LIST),
    ),
    'oeuvre': (
        Rel('dedicaces', 'dedicace', 'oeuvre',
            list_keys=('dedicataires', 'dedicataire'), other='individu',
            modes=LIST),
        Rel('pupitres', 'pupitre', 'oeuvre', ids_key='pupitres',
            modes=((D(2015, 3, 30), 'ids'), (None, 'followed'))),
        Rel('parentes_meres', 'parentedoeuvres', 'fille', modes=FOLLOWED),
        Rel('auteurs', 'auteur', 'oeuvre', gfk='oeuvre', ids_key='auteurs',
            modes=((D(2012, 10, 17), 'ids'), (None, 'followed'))),
    ),
    'partie': (
        Rel('partieprofession_set', 'partieprofession', 'partie',
            list_keys=('professions',), other='profession', modes=LIST),
    ),
    'profession': (),
    'lieu': (),
    'ensemble': (
        Rel('membres', 'membre', 'ensemble', modes=FOLLOWED),
    ),
    'source': (
        Rel('sourceevenement_set', 'sourceevenement', 'source',
            list_keys=('evenements',), other='evenement', modes=SOURCE_LINK),
        Rel('sourceoeuvre_set', 'sourceoeuvre', 'source', modes=SOURCE_LINK),
        Rel('sourceindividu_set', 'sourceindividu', 'source',
            modes=SOURCE_LINK),
        Rel('sourceensemble_set', 'sourceensemble', 'source',
            modes=SOURCE_LINK),
        Rel('sourcelieu_set', 'sourcelieu', 'source', modes=SOURCE_LINK),
        Rel('sourcepartie_set', 'sourcepartie', 'source', modes=SOURCE_LINK),
        Rel('sourceuser_set', 'sourceuser', 'source',
            list_keys=('editeurs_scientifiques',), other='user', modes=LIST),
        Rel('auteurs', 'auteur', 'source', gfk='source', ids_key='auteurs',
            modes=((D(2012, 10, 17), 'ids'), (None, 'followed'))),
    ),
}
RELS['audio'] = RELS['video'] = RELS['source']

FAMILIES = {
    'evenement': ('evenement',),
    'individu': ('individu',),
    'oeuvre': ('oeuvre',),
    'partie': ('partie',),
    'profession': ('profession',),
    'lieu': ('lieu',),
    'ensemble': ('ensemble',),
    'source': ('source', 'audio', 'video'),
}


def model_of(name):
    return apps.get_model('libretto', name)


def load_json(raw):
    """(data, flag). Some old snapshots lost the backslash of ``=\\"\\"``."""
    try:
        return json.loads(raw), None
    except ValueError:
        pass
    fixed = re.sub(r'(?<!\\)=""', r'=\\"\\"', raw)
    try:
        return json.loads(fixed), 'repaired_json'
    except ValueError:
        pass
    try:
        return json.JSONDecoder().raw_decode(fixed)[0], 'repaired_json'
    except ValueError:
        return None, 'invalid_json'


def read_snapshot(raw):
    """(pk, fields, flag), or (None, None, reason) if unreadable."""
    data, flag = load_json(raw)
    if data is None:
        return None, None, flag
    try:
        item = data[0]
        return item['pk'], item['fields'], flag
    except (KeyError, IndexError, TypeError):
        return None, None, 'bad_shape'


class Context:
    """What the builders share: lookups, caches and the problems met."""

    def __init__(self):
        self.cts = {}
        self.unknown = Counter()
        self._pupitre_partie = None
        self.flags = set()
        self.date = None
        self.started = timezone.now()
        self.reset_batch()

    def reset_batch(self):
        self.timelines = {}  # (model name, pk) -> [(date, rev id, fields)]
        self.bad = set()     # (model name, pk) with an unreadable version
        self.alive = {}      # (model name, pk) -> does the row still exist?
        self.lines = {}      # (model name, line pk) -> pks of cast rows
        self.live = {}       # (model name, pk) -> live row, or None
        self.missing = defaultdict(set)
        self.dirty = False

    def ct(self, name):
        if name not in self.cts:
            self.cts[name] = ContentType.objects.get_for_model(
                model_of(name), for_concrete_model=False).pk
        return self.cts[name]

    @property
    def pupitre_partie(self):
        if self._pupitre_partie is None:
            self._pupitre_partie = dict(
                model_of('pupitre').objects.values_list('pk', 'partie_id'))
        return self._pupitre_partie

    # The lookups below fill ``missing`` when the batch did not load the
    # thing yet. The caller loads it and builds again.

    def timeline(self, name, pk):
        if (name, pk) not in self.timelines:
            self.missing['timeline'].add((name, pk))
            self.dirty = True
            return []
        return self.timelines[(name, pk)]

    def version_at(self, name, pk, key):
        found = None
        for date, revision_id, fields in self.timeline(name, pk):
            if (date, revision_id) > key:
                break
            found = fields
        return found

    def line_rows(self, name, line_pk):
        if (name, line_pk) not in self.lines:
            self.missing['line'].add((name, line_pk))
            self.dirty = True
            return []
        return self.lines[(name, line_pk)]

    def live_row(self, name, pk):
        if (name, pk) not in self.live:
            self.missing['live'].add((name, pk))
            self.dirty = True
            return None
        return self.live[(name, pk)]


def scalar(ctx, model, pk, fields, renames=None, **overrides):
    """The snapshot as ``serializable_data()`` writes it, without the rows."""
    renames = renames or {}
    fields = {renames.get(k, k): v for k, v in fields.items()}
    fields.update(overrides)
    kwargs = {}
    for field in model._meta.concrete_fields:
        name = field.name
        if name == 'latest_revision' or field.primary_key or (
                not field.serialize):
            continue
        if field.is_relation and field.many_to_one:
            kwargs[field.attname] = fields.get(name)
        elif name in fields:
            value = fields[name]
            if hasattr(field, 'geom_type'):
                try:
                    kwargs[name] = GEOSGeometry(value) if value else None
                except Exception:
                    ctx.flags.add('lost:%s' % name)
                    kwargs[name] = None
                continue
            if value is None and not field.null:
                # Written by a generation of the model that allowed it.
                kwargs[name] = field.get_default()
                continue
            try:
                kwargs[name] = field.to_python(value)
            except Exception:
                ctx.flags.add('lost:%s' % name)
                kwargs[name] = field.get_default()
        else:
            kwargs[name] = field.get_default()
    obj = model(**kwargs)
    # Both: the primary key of a multi-table child is its parent link.
    obj.pk = pk
    if model._meta.parents and hasattr(obj, 'id'):
        obj.id = pk
    data = serializable_data(obj)
    # A field the snapshot does not have did not exist yet. Its key stays
    # out of the copy, so that a revert leaves today's value alone.
    for name in [n for n in data if n not in fields]:
        if name not in ('pk', 'latest_revision'):
            del data[name]
    return data


def field_value(field, obj):
    # modelcluster's get_field_value calls pre_save, which makes autoslug
    # build a missing slug from the database. A snapshot must not.
    if field.remote_field is not None:
        return getattr(obj, field.get_attname())
    value = getattr(obj, field.attname)
    if isinstance(value, datetime.datetime) and settings.USE_TZ:
        if timezone.is_naive(value):
            value = timezone.make_aware(
                value, timezone.get_default_timezone(),
            ).astimezone(datetime.timezone.utc)
        else:
            value = timezone.localtime(value, datetime.timezone.utc)
    if is_protected_type(value):
        return value
    return field.value_to_string(obj)


def serializable_data(obj):
    """What modelcluster's ``get_serializable_data_for_fields`` writes."""
    pk_field = obj._meta.pk
    while pk_field.remote_field and pk_field.remote_field.parent_link:
        pk_field = pk_field.remote_field.model._meta.pk
    data = {'pk': field_value(pk_field, obj)}
    for field in obj._meta.fields:
        if field.serialize:
            data[field.name] = field_value(field, obj)
    return data


def sort_rows(model, rows):
    names = [o.lstrip('-') for o in model._meta.ordering
             if o.lstrip('-') in {f.name for f in model._meta.fields}]

    def key(row):
        return tuple(
            (row.get(n) is None, row.get(n) if row.get(n) is not None else 0)
            for n in names
        ) + ((row['pk'] is None, row['pk'] or 0),)
    try:
        return sorted(rows, key=key)
    except TypeError:
        return sorted(rows, key=lambda r: (r['pk'] is None, r['pk'] or 0))


def distribution_rows(ctx, rel, parent_pk, pk, fields):
    """New-style rows are one to one. Old ones list people and ensembles."""
    model = model_of('elementdedistribution')
    parent_fields = {'evenement': None, 'element_de_programme': None}
    parent_fields[rel.fk] = parent_pk
    old = 'individus' in fields or 'ensembles' in fields or 'pupitre' in fields
    if not old:
        return [scalar(ctx, model, pk, fields, **parent_fields)]
    partie = None
    if fields.get('pupitre'):
        partie = ctx.pupitre_partie.get(fields['pupitre'])
        if partie is None:
            ctx.flags.add('lost:pupitre')
    targets = (
        [('individu', i) for i in fields.get('individus') or []]
        + [('ensemble', e) for e in fields.get('ensembles') or []]
    ) or [(None, None)]
    rows = []
    for n, (side, value) in enumerate(targets):
        data = {
            'owner': fields.get('owner'), 'partie': partie,
            'individu': None, 'ensemble': None, 'profession': None,
            **parent_fields}
        if side:
            data[side] = value
        rows.append(scalar(ctx, model, pk if n == 0 else None, data))
    return rows


def follows(rel, parent_pk, ctx, fields):
    if fields.get(rel.fk) == parent_pk:
        return True
    return bool(
        rel.gfk and fields.get('content_type') == ctx.ct(rel.gfk)
        and fields.get('object_id') == parent_pk)


def make_rows(ctx, rel, parent_pk, pk, fields):
    if rel.expand == 'distribution':
        return distribution_rows(ctx, rel, parent_pk, pk, fields)
    if rel.model == 'parentedindividus' and not fields.get('parent'):
        ctx.flags.add('lost:parente')
        return []
    return [scalar(
        ctx, model_of(rel.model), pk, fields, **{rel.fk: parent_pk})]


def with_nested(ctx, rel, built, fields, versions, claimed, key):
    for row in built:
        for nested in rel.nested:
            row[nested.name] = child_rows(
                ctx, nested, row['pk'], fields, versions, claimed, key,
            ) if row['pk'] is not None else []
    return built


def child_rows(ctx, rel, parent_pk, parent_fields, versions, claimed, key):
    """The rows of a relation in the revision at ``key`` (date, id)."""
    model = model_of(rel.model)
    mode = rel.mode(key[0].date())
    rows = []
    if mode == 'followed':
        for pk, fields, _flag in versions.get(rel.model, ()):
            if (rel.model, pk) in claimed:
                continue
            if not follows(rel, parent_pk, ctx, fields):
                continue
            claimed.add((rel.model, pk))
            rows += with_nested(ctx, rel, make_rows(
                ctx, rel, parent_pk, pk, fields), fields, versions, claimed,
                key)
    elif mode == 'ids':
        for pk in parent_fields.get(rel.ids_key) or []:
            if (rel.model, pk) in claimed:
                continue
            fields = ctx.version_at(rel.model, pk, key)
            if (rel.model, pk) not in ctx.timelines:
                continue  # not loaded yet, the caller builds again
            if (rel.model, pk) in ctx.bad:
                ctx.flags.add('child_unreadable')
                continue
            if fields is not None:
                built = make_rows(ctx, rel, parent_pk, pk, fields)
            else:
                # No version by then: it was edited on its own page after.
                live = ctx.live_row(rel.model, pk)
                if (rel.model, pk) not in ctx.live:
                    continue
                if live is None:
                    ctx.flags.add('unknown_row:%s' % rel.path)
                    continue
                ctx.flags.add('content_from_live')
                built = [{**live, rel.fk: parent_pk}]
            claimed.add((rel.model, pk))
            rows += with_nested(
                ctx, rel, built, fields or {}, versions, claimed, key)
    elif mode == 'nested':
        for pk in ctx.line_rows(rel.model, parent_pk):
            if (rel.model, pk) in claimed or (rel.model, pk) not in ctx.timelines:
                continue
            timeline = ctx.timelines[(rel.model, pk)]
            if (rel.model, pk) in ctx.bad:
                ctx.flags.add('child_unreadable')
            if not timeline or timeline[0][:2] > key:
                continue  # not created yet
            fields = ctx.version_at(rel.model, pk, key)
            if fields.get(rel.fk) != parent_pk:
                continue
            gone = not ctx.alive.get((rel.model, pk), True)
            claimed.add((rel.model, pk))
            # A row that is gone today was deleted at some save after its
            # last version. The old admin did not record it.
            if gone and timeline[-1][:2] < key:
                ctx.flags.add('deleted_unknown:%s' % rel.path)
            rows += make_rows(ctx, rel, parent_pk, pk, fields)
    elif mode == 'list':
        for list_key in rel.list_keys:
            value = parent_fields.get(list_key)
            if value is None:
                continue
            for other in (value if isinstance(value, list) else [value]):
                row = scalar(ctx, model, None, {
                    rel.fk: parent_pk, rel.other: other})
                for nested in rel.nested:
                    row[nested.name] = []
                rows.append(row)
    return sort_rows(model, rows)


def prescan(ctx, rels, parent_pk, parent_fields, versions, key):
    """Asks for what the revision will need, so that one load serves all."""
    for rel in rels:
        mode = rel.mode(key[0].date())
        if mode == 'ids':
            for pk in parent_fields.get(rel.ids_key) or []:
                ctx.timeline(rel.model, pk)
        elif mode == 'nested':
            ctx.line_rows(rel.model, parent_pk)
        elif mode == 'followed' and rel.nested:
            for pk, fields, _flag in versions.get(rel.model, ()):
                if follows(rel, parent_pk, ctx, fields):
                    prescan(ctx, rel.nested, pk, fields, versions, key)


def build_content(ctx, label, pk, fields, versions, key):
    """The content of the Wagtail revision."""
    model = model_of(label)
    content = scalar(ctx, model, pk, fields, RENAMES.get(label))
    claimed = set()
    for lost_key in LOST_KEYS.get(label, ()):
        if fields.get(lost_key) is not None:
            ctx.flags.add('lost:ancrage')
    known = {f.name for f in model._meta.fields} | set(
        RENAMES.get(label, ())) | DROPPED
    for field_name in fields:
        if field_name not in known:
            ctx.unknown[(label, field_name)] += 1
    for rel in RELS[label]:
        content[rel.name] = child_rows(
            ctx, rel, pk, fields, versions, claimed, key)
    return content


def fix_row_ids(ctx, contents):
    """
    A row id that now belongs to another parent must not be reused: restoring
    it would move that other row. The row becomes a new one instead. Rows
    that were never versioned (links made from a list) take the id of the
    live row with the same two sides, if there is one, so a restore keeps
    them. Each revision takes its own ids: two revisions both hold the link.
    """
    wanted = defaultdict(list)  # (model name, fk name) -> [(row, parent pk)]
    links = defaultdict(list)   # (model, fk, other) -> [(content no, row, parent)]

    def walk(number, rows, rel, parent_pk):
        for row in rows:
            if row['pk'] is not None:
                wanted[(rel.model, rel.fk)].append((row, parent_pk))
            elif rel.other:
                links[(rel.model, rel.fk, rel.other)].append(
                    (number, row, parent_pk))
            for nested in rel.nested:
                if row['pk'] is not None:
                    walk(number, row.get(nested.name, ()), nested, row['pk'])
    for number, (label, content) in enumerate(contents):
        for rel in RELS[label]:
            walk(number, content[rel.name], rel, content['pk'])
    for (name, fk), items in wanted.items():
        model = model_of(name)
        owners = dict(model._base_manager.filter(
            pk__in={row['pk'] for row, _ in items},
        ).values_list('pk', fk))
        for row, parent_pk in items:
            if row['pk'] in owners and owners[row['pk']] != parent_pk:
                row['pk'] = None
    for (name, fk, other), items in links.items():
        model = model_of(name)
        live = defaultdict(list)
        for pk, parent, side in model._base_manager.filter(
                **{fk + '__in': {parent for _, _, parent in items}},
        ).values_list('pk', fk, other):
            live[(parent, side)].append(pk)
        taken = defaultdict(set)  # content no -> ids it already uses
        for number, row, parent_pk in items:
            for pk in live.get((parent_pk, row[other]), ()):
                if pk not in taken[number]:
                    taken[number].add(pk)
                    row['pk'] = pk
                    break


# --- Orchestration --------------------------------------------------------

def current_pks(family):
    """pk -> model name of the objects of a family that still exist."""
    pks = {}
    for name in FAMILIES[family]:
        model = model_of(name)
        for pk in model._base_manager.values_list('pk', flat=True):
            pks[pk] = name
    # Audio and Video are Source rows too: the most specific name comes last
    # and wins.
    return pks


def pk_models(family, names_cts):
    """
    (pk -> model name, pks that exist, pks that have history). Deleted
    objects take the most specific model that appears in their versions.
    """
    existing = current_pks(family)
    models = dict(existing)
    names = {names_cts[n]: n for n in FAMILIES[family]}
    order = {n: i for i, n in enumerate(FAMILIES[family])}
    with_history = set()
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT DISTINCT object_id, content_type_id FROM reversion_version'
            ' WHERE content_type_id = ANY(%s)', [list(names)])
        for object_id, ct in cursor.fetchall():
            pk = int(object_id)
            with_history.add(pk)
            if pk not in existing and (
                    pk not in models or order[names[ct]] > order[models[pk]]):
                models[pk] = names[ct]
    return models, set(existing), with_history


def fetch(batch_pks, family, names_cts):
    parent_cts = [names_cts[n] for n in FAMILIES[family]]
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT DISTINCT revision_id FROM reversion_version '
            'WHERE content_type_id = ANY(%s) AND object_id = ANY(%s)',
            [parent_cts, [str(p) for p in batch_pks]])
        revision_ids = [r[0] for r in cursor.fetchall()]
        cursor.execute(
            'SELECT id, date_created, user_id, comment FROM reversion_revision'
            ' WHERE id = ANY(%s)', [revision_ids])
        revisions = {r[0]: r[1:] for r in cursor.fetchall()}
        cursor.execute(
            'SELECT revision_id, content_type_id, object_id, object_repr, '
            'serialized_data FROM reversion_version '
            'WHERE revision_id = ANY(%s) AND content_type_id = ANY(%s)',
            [revision_ids, list(names_cts.values())])
        rows = cursor.fetchall()
    return revisions, rows


def related_names(label, rels=None):
    names = set()
    for rel in RELS[label] if rels is None else rels:
        names.add(rel.model)
        names |= related_names(label, rel.nested)
    return names


def content_type_ids(family):
    names = set(FAMILIES[family])
    for name in FAMILIES[family]:
        names |= related_names(name)
    return {
        name: ContentType.objects.get_for_model(
            model_of(name), for_concrete_model=False).pk
        for name in names
    }


def base_content_type(model):
    parents = model._meta.get_parent_list()
    return ContentType.objects.get_for_model(
        parents[-1] if parents else model, for_concrete_model=False)


# --- Loading what a batch needs ---------------------------------------------

def ensure_cast_index(names_cts):
    """
    A session table of which cast rows ever pointed at which programme line.
    Finding them in the snapshots one line at a time would scan the table.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass('pg_temp.reversion_cast_index')")
        if cursor.fetchone()[0]:
            return
        cursor.execute(
            'CREATE TEMP TABLE reversion_cast_index AS SELECT '
            'object_id::int AS row_pk, (substring(serialized_data FROM '
            '\'"element_de_programme": ([0-9]+)\'))::int AS line_pk '
            'FROM reversion_version WHERE content_type_id = %s AND '
            'serialized_data ~ \'"element_de_programme": [0-9]\'',
            [names_cts['elementdedistribution']])
        cursor.execute(
            'CREATE INDEX ON reversion_cast_index (line_pk)')


def load_timelines(ctx, names_cts, name, pks):
    for pk in pks:
        ctx.timelines[(name, pk)] = []
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT v.object_id, v.revision_id, r.date_created, '
            'v.serialized_data FROM reversion_version v JOIN '
            'reversion_revision r ON r.id = v.revision_id WHERE '
            'v.content_type_id = %s AND v.object_id = ANY(%s)',
            [names_cts[name], [str(pk) for pk in pks]])
        for object_id, revision_id, date, raw in cursor.fetchall():
            pk = int(object_id)
            data_pk, fields, _flag = read_snapshot(raw)
            if data_pk is None:
                ctx.bad.add((name, pk))
                continue
            ctx.timelines[(name, pk)].append((date, revision_id, fields))
    for pk in pks:
        ctx.timelines[(name, pk)].sort(key=lambda v: v[:2])
    alive = set(model_of(name)._base_manager.filter(
        pk__in=pks).values_list('pk', flat=True))
    for pk in pks:
        ctx.alive[(name, pk)] = pk in alive


def load_live_rows(ctx, name, pks):
    model = model_of(name)
    found = {o.pk: serializable_data(o)
             for o in model._base_manager.filter(pk__in=pks)}
    for pk in pks:
        ctx.live[(name, pk)] = found.get(pk)


def resolve_missing(ctx, names_cts):
    """Loads what the builders asked for. Returns False if nothing was."""
    missing, ctx.missing = ctx.missing, defaultdict(set)
    if not any(missing.values()):
        return False
    timelines = defaultdict(set)
    for name, pk in missing['timeline']:
        timelines[name].add(pk)
    lines = defaultdict(set)
    for name, line_pk in missing['line']:
        lines[name].add(line_pk)
    for name, line_pks in lines.items():
        ensure_cast_index(names_cts)
        for line_pk in line_pks:
            ctx.lines[(name, line_pk)] = []
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT DISTINCT row_pk, line_pk FROM reversion_cast_index '
                'WHERE line_pk = ANY(%s)', [list(line_pks)])
            for row_pk, line_pk in cursor.fetchall():
                ctx.lines[(name, line_pk)].append(row_pk)
                timelines[name].add(row_pk)
    for name, pks in timelines.items():
        load_timelines(ctx, names_cts, name, sorted(pks))
    live = defaultdict(set)
    for name, pk in missing['live']:
        live[name].add(pk)
    for name, pks in live.items():
        load_live_rows(ctx, name, sorted(pks))
    return True


# --- Reading a batch ----------------------------------------------------------

def read_batch(ctx, family, batch, pk_model, names_cts):
    """Entries (one per old version of an object) for a batch of objects."""
    ctx.reset_batch()
    ct_names = {ct: name for name, ct in names_cts.items()}
    revisions, rows = fetch(batch, family, names_cts)
    by_revision = defaultdict(lambda: defaultdict(list))
    reprs = {}
    unreadable = defaultdict(Counter)
    bad_children = Counter()
    for revision_id, ct, object_id, object_repr, raw in rows:
        name = ct_names[ct]
        pk, fields, flag = read_snapshot(raw)
        is_parent = name in FAMILIES[family]
        if pk is None:
            if is_parent:
                unreadable[revision_id][(name, int(object_id))] = flag
            else:
                bad_children[revision_id] += 1
            continue
        by_revision[revision_id][name].append((pk, fields, flag))
        if is_parent:
            reprs[(revision_id, int(object_id))] = object_repr
    batch_pks = set(batch)
    objects = defaultdict(list)
    for revision_id in set(by_revision) | set(unreadable):
        by_name = by_revision.get(revision_id, {})
        for name in FAMILIES[family]:
            for pk, fields, flag in by_name.get(name, ()):
                if pk in batch_pks and pk in pk_model:
                    objects[pk].append((revision_id, name, fields, flag))
        for (name, pk), flag in unreadable.get(revision_id, {}).items():
            if pk in batch_pks and pk in pk_model:
                objects[pk].append((revision_id, name, None, flag))
    entries = {}
    specs = []
    for pk, versions in objects.items():
        label = pk_model[pk]
        merged = {}
        for revision_id, name, fields, flag in versions:
            slot = merged.setdefault(revision_id, {'flags': set()})
            if fields is None:
                slot['bad'] = flag
                continue
            slot.setdefault('fields', {}).update(fields)
            if flag:
                slot['flags'].add(flag)
        result = []
        for revision_id, slot in merged.items():
            date, user_id, comment = revisions[revision_id]
            entry = {
                'pk': pk, 'label': label, 'revision_id': revision_id,
                'date': date, 'user_id': user_id, 'comment': comment,
                'repr': reprs.get((revision_id, pk), ''),
                'content': None, 'flags': set(slot['flags']),
                'reason': slot.get('bad') if 'fields' not in slot else None,
            }
            if 'fields' in slot:
                specs.append((
                    entry, slot, by_revision[revision_id],
                    (date, revision_id)))
            result.append(entry)
        result.sort(key=lambda e: (e['date'], e['revision_id']))
        entries[pk] = result
    for entry, slot, versions, key in specs:
        prescan(ctx, RELS[entry['label']], entry['pk'], slot['fields'],
                versions, key)
    resolve_missing(ctx, names_cts)
    todo = specs
    for _round in range(4):
        again = []
        for spec in todo:
            entry, slot, versions, key = spec
            entry['flags'] = set(slot['flags'])
            ctx.flags = entry['flags']
            ctx.date = key[0].date()
            ctx.dirty = False
            try:
                entry['content'] = build_content(
                    ctx, entry['label'], entry['pk'], slot['fields'],
                    versions, key)
            except Exception as e:  # keep the change in the History list
                entry['content'] = None
                entry['reason'] = 'build_error:%s' % type(e).__name__
            if ctx.dirty:
                again.append(spec)
                continue
            if bad_children[key[1]] and entry['content']:
                entry['flags'].add('child_unreadable')
        if not again:
            break
        resolve_missing(ctx, names_cts)
        todo = again
    return entries


REASON_PREFIXES = ('lost:', 'unknown_row:')


def mark_doubtful(entries):
    """
    A revision is doubtful when a state could not be rebuilt: lost fields,
    rows that cannot be found. It is only uncertain when a row may have been
    deleted already: the old admin did not record deletions. An empty
    followed relation is a real state, never a doubt.
    """
    for entry in entries:
        entry['reasons'] = sorted(
            {f for f in entry['flags'] if f.startswith(REASON_PREFIXES)}
            | ({'child_unreadable'} & entry['flags']))
        entry['uncertain'] = sorted(
            f for f in entry['flags'] if f.startswith('deleted_unknown:'))


# --- The live objects -------------------------------------------------------

def live_rows_for(rel, parent_pks):
    """{parent pk: [rows]} of the live rows, with their own children."""
    model = model_of(rel.model)
    rows = [serializable_data(i) for i in model._base_manager.filter(
        **{rel.fk + '__in': list(parent_pks)})]
    by_pk = {row['pk']: row for row in rows}
    for nested in rel.nested:
        sub = live_rows_for(nested, set(by_pk)) if by_pk else {}
        for pk, row in by_pk.items():
            row[nested.name] = sub.get(pk, [])
    grouped = defaultdict(list)
    for row in rows:
        grouped[row[rel.fk]].append(row)
    return grouped


def live_contents(label, pks):
    """pk -> content of the live object, as a revision would hold it."""
    model = model_of(label)
    objs = {o.pk: o for o in model._base_manager.filter(pk__in=list(pks))}
    contents = {pk: serializable_data(o) for pk, o in objs.items()}
    for rel in RELS[label]:
        grouped = live_rows_for(rel, set(objs)) if objs else {}
        for pk, content in contents.items():
            content[rel.name] = grouped.get(pk, [])
    return contents, objs


def canonical(content):
    """Content as JSON, rows in a fixed order, ``latest_revision`` aside."""
    value = json.loads(json.dumps(content, cls=DjangoJSONEncoder))

    def norm(x):
        if isinstance(x, dict):
            return {k: norm(v) for k, v in x.items()}
        if isinstance(x, list):
            return sorted((norm(i) for i in x),
                          key=lambda i: json.dumps(i, sort_keys=True))
        return x
    value = norm(value)
    value.pop('latest_revision', None)
    return value


def contains(old, new):
    """
    Is ``old`` what ``new`` says, for every key ``old`` has? A key that
    ``old`` lacks is a field that did not exist then: it is not a difference.
    Rows are matched by pk, at every level.
    """
    if isinstance(old, dict):
        return isinstance(new, dict) and all(
            key in new and contains(value, new[key])
            for key, value in old.items())
    if isinstance(old, list):
        if not isinstance(new, list) or len(old) != len(new):
            return False
        if all(isinstance(r, dict) and r.get('pk') is not None
               for r in old + new):
            by_pk = {r['pk']: r for r in new}
            return len(by_pk) == len(new) and all(
                r['pk'] in by_pk and contains(r, by_pk[r['pk']]) for r in old)
        return old == new
    return old == new


def differences(old, new):
    """The top-level keys of ``old`` that ``new`` does not agree with."""
    old, new = canonical(old), canonical(new)
    return sorted(k for k, v in old.items()
                  if k not in new or not contains(v, new[k]))


# --- Writing --------------------------------------------------------------

def already_imported(family, batch, names_cts):
    cts = [names_cts[n] for n in FAMILIES[family]]
    return set(ModelLogEntry.objects.filter(
        content_type_id__in=cts, object_id__in=[str(p) for p in batch],
        data__has_key='reversion_revision_id',
    ).values_list('object_id', 'data__reversion_revision_id'))


def write_batch(
        ctx, entries_by_pk, family, user_ids, names_cts, stats, existing=()):
    """Revisions then log entries, in date order so that ids follow dates."""
    done = already_imported(family, list(entries_by_pk), names_cts)
    new = []
    for pk, entries in entries_by_pk.items():
        mark_doubtful(entries)
        for n, entry in enumerate(entries):
            if (str(pk), entry['revision_id']) in done:
                stats['skipped'] += 1
                continue
            new.append((entry, n == 0))
    new.sort(key=lambda x: (x[0]['date'], x[0]['revision_id']))
    cts = {}

    def types(label):
        if label not in cts:
            model = model_of(label)
            cts[label] = (
                ContentType.objects.get_for_model(
                    model, for_concrete_model=False).pk,
                base_content_type(model).pk)
        return cts[label]
    revisions = []
    for entry, _ in new:
        if entry['content'] is not None:
            user_id = entry['user_id'] if entry['user_id'] in user_ids else None
            content_type, base = types(entry['label'])
            revisions.append(Revision(
                content_type_id=content_type, base_content_type_id=base,
                object_id=str(entry['pk']), created_at=entry['date'],
                user_id=user_id, object_str=entry['repr'],
                content=entry['content']))
            entry['revision'] = revisions[-1]
    Revision.objects.bulk_create(revisions, batch_size=200)
    logs = []
    for entry, first in new:
        user_id = entry['user_id'] if entry['user_id'] in user_ids else None
        data = {
            'imported_from': 'reversion',
            'reversion_revision_id': entry['revision_id'],
            'comment': entry['comment'],
            'doubtful': bool(entry['reasons']),
            'doubtful_reasons': entry['reasons'],
            'uncertain': bool(entry['uncertain']),
            'uncertain_reasons': entry['uncertain'],
            'flags': sorted(entry['flags']),
        }
        revision = entry.get('revision')
        if revision is None:
            data['snapshot_unreadable'] = True
            data['reason'] = entry['reason']
            stats['log_only'] += 1
            stats['log_only:%s' % entry['reason']] += 1
        else:
            stats['revisions'] += 1
        if 'content_from_live' in entry['flags']:
            stats['content_from_live'] += 1
        if entry['reasons']:
            stats['doubtful'] += 1
            for reason in entry['reasons']:
                stats['doubtful:%s' % reason] += 1
        if entry['uncertain']:
            stats['uncertain'] += 1
            for reason in entry['uncertain']:
                stats['uncertain:%s' % reason] += 1
        added = entry['comment'].startswith(('Ajout', '[{"added": {}}'))
        created = is_initial(entry['comment']) or (first and added)
        logs.append(ModelLogEntry(
            content_type_id=types(entry['label'])[0],
            object_id=str(entry['pk']), label=entry['repr'] or str(entry['pk']),
            action=ACTION_CREATE if created else ACTION_EDIT,
            timestamp=entry['date'], data=data, user_id=user_id,
            revision_id=revision.pk if revision else None,
            content_changed=True))
    ModelLogEntry.objects.bulk_create(logs, batch_size=500)
    finish_objects(ctx, entries_by_pk, existing, types, stats)


def finish_objects(ctx, entries_by_pk, existing, types, stats):
    """
    Wagtail takes the newest revision of an object as its current state. If
    the newest imported revision is today's data, the object points to it.
    If not (a script wrote to it, or the old admin did not record the edit),
    one more revision holds today's data.
    """
    by_label = defaultdict(list)
    for pk, entries in entries_by_pk.items():
        if pk in existing and entries:
            by_label[entries[0]['label']].append(pk)
    copies = []
    point = defaultdict(list)  # model name -> [(object, revision)]
    for label, pks in by_label.items():
        contents, objs = live_contents(label, pks)
        for pk in pks:
            obj, live = objs.get(pk), contents.get(pk)
            newest = entries_by_pk[pk][-1]
            if obj is None:
                continue
            if obj.latest_revision_id is not None:
                # Already has a revision made by Wagtail itself.
                stats['native_latest'] += 1
                continue
            revision = newest.get('revision')
            if revision is None and newest['content'] is not None:
                continue  # skipped by an earlier run
            differs = (
                ['newest_unreadable'] if newest['content'] is None
                else differences(newest['content'], live))
            if not differs:
                point[label].append((obj, revision))
                stats['latest_set'] += 1
                continue
            live['latest_revision'] = None
            content_type, base = types(label)
            copy = Revision(
                content_type_id=content_type, base_content_type_id=base,
                object_id=str(pk), created_at=ctx.started, user_id=None,
                object_str=str(obj), content=live)
            copies.append((label, obj, copy, differs, newest))
    Revision.objects.bulk_create([c[2] for c in copies], batch_size=200)
    logs = []
    for label, obj, copy, differs, newest in copies:
        point[label].append((obj, copy))
        stats['today_copies'] += 1
        stats['today_copies:%s' % label] += 1
        for key in differs:
            stats['today_differs:%s:%s' % (label, key)] += 1
        logs.append(ModelLogEntry(
            content_type_id=types(label)[0], object_id=str(obj.pk),
            label=copy.object_str or str(obj.pk), action=ACTION_TODAY,
            timestamp=ctx.started, user_id=None, revision_id=copy.pk,
            content_changed=True, data={
                'imported_from': 'reversion', 'today_copy': True,
                'doubtful': False, 'doubtful_reasons': [], 'flags': [],
                'differs': differs[:12],
                'newest_reversion_revision_id': newest['revision_id'],
            }))
    ModelLogEntry.objects.bulk_create(logs, batch_size=500)
    for label, pairs in point.items():
        objs = []
        for obj, revision in pairs:
            obj.latest_revision_id = revision.pk
            objs.append(obj)
        model_of(label)._base_manager.bulk_update(
            objs, ['latest_revision'], batch_size=300)


# --- Running it -------------------------------------------------------------

def pending(family, names_cts, pks):
    """The objects that still have old revisions to import, and the others."""
    cts = [names_cts[n] for n in FAMILIES[family]]
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT object_id, count(DISTINCT revision_id) FROM '
            'reversion_version WHERE content_type_id = ANY(%s) '
            'GROUP BY object_id', [cts])
        total = {int(o): n for o, n in cursor.fetchall()}
    done = Counter()
    for object_id in ModelLogEntry.objects.filter(
            content_type_id__in=cts, data__has_key='reversion_revision_id',
    ).values_list('object_id', flat=True):
        done[int(object_id)] += 1
    todo = [pk for pk in pks if done[pk] < total.get(pk, 0)]
    return todo, len(pks) - len(todo)


def import_family(
        family, *, sample=None, only=None, batch_size=300, dry_run=False,
        progress=None, ctx=None):
    """Import the history of every object of a family. Returns the stats."""
    from django.contrib.auth import get_user_model
    from django.db import transaction

    stats = Counter()
    ctx = ctx or Context()
    names_cts = content_type_ids(family)
    pk_model, existing, with_history = pk_models(family, names_cts)
    pks = sorted(with_history)
    if only:
        pks = [pk for pk in pks if pk in set(only)]
    stats['objects_with_history'] = len(with_history)
    if sample:
        # A fixed shuffle, so that two sample runs see the same objects.
        pks = sorted(pks, key=lambda pk: (pk * 2654435761) % 2 ** 32)[:sample]
        pks.sort()
    pks, stats['objects_done'] = pending(family, names_cts, pks)
    user_ids = set(get_user_model().objects.values_list('pk', flat=True))
    stats['objects'] = len(pks)
    stats['deleted_objects'] = len([pk for pk in pks if pk not in existing])
    # Each batch commits on its own, so an interrupted run can be resumed. A
    # dry run wraps everything in one transaction and rolls it back.
    with transaction.atomic() if dry_run else nullcontext():
        for start in range(0, len(pks), batch_size):
            batch = pks[start:start + batch_size]
            with transaction.atomic():
                entries = read_batch(ctx, family, batch, pk_model, names_cts)
                fix_row_ids(
                    ctx, [(e['label'], e['content'])
                          for es in entries.values() for e in es
                          if e['content'] is not None])
                write_batch(
                    ctx, entries, family, user_ids, names_cts, stats, existing)
            if progress:
                progress(family, min(start + batch_size, len(pks)), len(pks),
                         stats)
        if dry_run:
            transaction.set_rollback(True)
    stats['unknown_keys'] = sum(ctx.unknown.values())
    return stats, ctx.unknown


def reset_imported(dry_run=False):
    """
    Deletes what an import made: its revisions and log entries. Revisions made
    by Wagtail itself stay. Returns the counts.
    """
    from django.db import transaction

    marked = (
        "action LIKE 'libretto.reversion.%' OR "
        "data ? 'reversion_revision_id'")
    counts = {}
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute(
            'CREATE TEMP TABLE imported_revisions ON COMMIT DROP AS SELECT '
            'DISTINCT revision_id AS id FROM wagtailcore_modellogentry '
            'WHERE (' + marked + ') AND revision_id IS NOT NULL')
        cursor.execute('SELECT count(*) FROM imported_revisions')
        counts['revisions'] = cursor.fetchone()[0]
        cursor.execute(
            'SELECT count(*) FROM wagtailcore_modellogentry WHERE ' + marked)
        counts['log_entries'] = cursor.fetchone()[0]
        for family in FAMILIES:
            table = model_of(FAMILIES[family][0])._meta.db_table
            cursor.execute(
                'UPDATE ' + table + ' SET latest_revision_id = NULL WHERE '
                'latest_revision_id IN (SELECT id FROM imported_revisions)')
            counts['latest_revision_cleared'] = counts.get(
                'latest_revision_cleared', 0) + cursor.rowcount
        cursor.execute(
            'DELETE FROM wagtailcore_modellogentry WHERE ' + marked)
        cursor.execute(
            'DELETE FROM wagtailcore_revision WHERE id IN '
            '(SELECT id FROM imported_revisions)')
        cts = [
            base_content_type(model_of(f[0])).pk for f in FAMILIES.values()]
        cursor.execute(
            'SELECT count(*) FROM wagtailcore_revision WHERE '
            'base_content_type_id = ANY(%s)', [cts])
        counts['wagtail_revisions_kept'] = cursor.fetchone()[0]
        if dry_run:
            transaction.set_rollback(True)
    return counts
