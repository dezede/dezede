import re
import warnings
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup
from bs4 import MarkupResemblesLocatorWarning

warnings.filterwarnings('ignore', category=MarkupResemblesLocatorWarning)

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError
from django.db import models
from django.utils.html import format_html
from tinymce.models import HTMLField

from .list_html_fields import DEFAULT_APP_LABELS, TAG_RE


# TODO: choisir comment gérer:
# cite
# - h1, h5, h6
# les alinea dans les paragraphes: <p style="padding-left: 30px;">
# les justifications: <p style="text-align: justify;">
# les trucs apparemment inutiles peut-être laissés par l’éditeur actuel:
# - <span style="text-align: start;"> / <p style="text-align: start;">
# - <span class="mce-nbsp-wrap">\xa0</span>
# les tables vides/avec une seule cellule


ALLOWED_BARE_TAGS = {
    'p', 'br', 'sup', 'em', 'strong', 'ul', 'ol', 'li', 'h2', 'h3', 'h4',
}
ALLOWED_ATTRS = {
    'span': {'class': ['sc']},
}
INTERNAL_LINK_HREF_RE = re.compile(
    r'<a href="(?:\.\./)+(?:'
    r'(?P<type>sources|individus|lieux-et-institutions|roles-et-instruments|ensembles|evenements|oeuvres)/id/(?P<pk>\d+)'
    r'|dossiers/id/(?P<dossier_pk>\d+)'
    r'|dossiers/(?P<slug>[\w%-]+)'
    r'|individus/(?P<individu_slug>[\w%-]+)'
    r'|oeuvres/(?P<oeuvre_slug>[\w%-]+)'
    r'|ensembles/(?P<ensemble_slug>[\w%-]+)'
    r'|lieux-et-institutions/(?P<lieu_slug>[\w%-]+)'
    r'|professions/(?P<profession_slug>[\w%-]+)'
    r'|utilisateurs/(?P<username>[\w.%-]+)'
    r')/?"[^>]*>'
)
INTERNAL_LINK_MODELS = {
    'sources': ('libretto', 'Source'),
    'individus': ('libretto', 'Individu'),
    'lieux-et-institutions': ('libretto', 'Lieu'),
    'roles-et-instruments': ('libretto', 'Partie'),
    'ensembles': ('libretto', 'Ensemble'),
    'evenements': ('libretto', 'Evenement'),
    'oeuvres': ('libretto', 'Oeuvre'),
}
DEZEDE_URL_PREFIX = 'https://dezede.org'


def build_snippet_link_html(obj, text, feature_name=None):
    ct = ContentType.objects.get_for_model(obj)
    feature_name = feature_name or f'{ct.model}-link'  # match wagtail_hooks.py registration
    return format_html(
        '<a linktype="{}" id="{}" data-string="{}" data-edit-link="" '
        'data-app-name="{}" data-model-name="{}">{}</a>',
        feature_name, obj.pk, str(obj), ct.app_label, ct.model, text,
    )


class UnexpectedTagError(Exception):
    pass


class Command(BaseCommand):
    help = (
        "Parses the HTML stored in a given field of a given model with "
        "BeautifulSoup, allowing/fixing a known set of tags and raising on "
        "any other tag."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'app_label', nargs='?',
            help=(
                "App label, e.g. 'libretto'. If omitted (along with "
                "model_name/field_name), every field reported by "
                "list_html_fields as containing HTML is processed."
            ),
        )
        parser.add_argument('model_name', nargs='?', help="Model name, e.g. 'Oeuvre'.")
        parser.add_argument(
            'field_name', nargs='?', help="Name of the field to inspect."
        )
        parser.add_argument(
            '--no-dry-run', action='store_false', dest='dry_run',
            help="Actually save the replaced values instead of just printing them.",
        )
        parser.add_argument(
            '--verbose', action='store_true',
            help="Also print each replaced tag (old -> new).",
        )

    def handle(self, *args, **options):
        app_label = options['app_label']
        model_name = options['model_name']
        field_name = options['field_name']
        dry_run = options['dry_run']
        verbose = options['verbose']

        if model_name and not app_label:
            raise CommandError('model_name requires app_label to be given as well.')
        if field_name and not model_name:
            raise CommandError('field_name requires model_name to be given as well.')

        if field_name:
            targets = [self._get_target(app_label, model_name, field_name)]
        else:
            targets = self._discover_html_fields(app_label, model_name)
            if not targets:
                self.stdout.write(self.style.WARNING('No HTML found in any field.'))
                return

        rows = 0
        changed = 0
        unexpected = 0
        for model, field in targets:
            f_rows, f_changed, f_unexpected = self._process_field(
                model, field, dry_run, verbose
            )
            rows += f_rows
            changed += f_changed
            unexpected += f_unexpected

        verb = 'would be replaced' if dry_run else 'replaced'
        self.stdout.write(
            self.style.SUCCESS(
                f'{rows} rows checked, {changed} rows {verb}, '
                f'{unexpected} rows with unexpected tags.'
            )
        )

    def _get_target(self, app_label, model_name, field_name):
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError as e:
            raise CommandError(f'Unknown model {model_name!r} in app {app_label!r}: {e}')

        try:
            field = model._meta.get_field(field_name)
        except Exception as e:
            raise CommandError(
                f'Unknown field {field_name!r} on {model._meta.label}: {e}'
            )

        if not isinstance(field, models.TextField):
            raise CommandError(
                f'{model._meta.label}.{field_name} is neither a TextField '
                'nor an HTMLField.'
            )

        return model, field

    def _discover_html_fields(self, app_label, model_name):
        if app_label:
            try:
                app_config = apps.get_app_config(app_label)
            except LookupError as e:
                raise CommandError(f'Unknown app {app_label!r}: {e}')
            models_list = list(app_config.get_models())
        else:
            models_list = [
                model for model in apps.get_models()
                if model._meta.app_label in DEFAULT_APP_LABELS
            ]

        if model_name:
            models_list = [m for m in models_list if m.__name__ == model_name]
            if not models_list:
                raise CommandError(
                    f'Unknown model {model_name!r} in app {app_label!r}.'
                )

        targets = []
        for model in models_list:
            for field in model._meta.get_fields():
                if not isinstance(field, models.TextField):
                    continue
                queryset = model._default_manager.values_list(
                    'pk', field.name
                ).iterator(chunk_size=1000)
                if any(value and TAG_RE.search(str(value)) for _, value in queryset):
                    targets.append((model, field))
        return targets

    def _process_field(self, model, field, dry_run, verbose):
        field_name = field.name

        field_type = 'HTMLField' if isinstance(field, HTMLField) else 'TextField'
        mode = 'Dry-run: validating' if dry_run else 'Validating and fixing'
        self.stdout.write(f'{mode} {model._meta.label}.{field_name} ({field_type})...')

        queryset = model._default_manager.values_list('pk', field_name).iterator(
            chunk_size=1000
        )
        rows = 0
        changed = 0
        unexpected = 0
        for pk, value in queryset:
            rows += 1
            if not value:
                continue
            try:
                replaced, new_value = self._validate(str(value))
            except UnexpectedTagError as e:
                unexpected += 1
                message = f'{model._meta.label}.{field_name} (pk={pk}): {e}'
                if dry_run:
                    self.stdout.write(self.style.WARNING(f'WARNING: {message}'))
                    continue
                raise CommandError(message)
            if not replaced:
                continue
            changed += 1
            if verbose:
                for old_tag, new_tag in replaced:
                    self.stdout.write(
                        f'{model._meta.label} (pk={pk}): {old_tag} -> {new_tag}'
                    )
            if not dry_run:
                model._default_manager.filter(pk=pk).update(**{field_name: new_value})

        return rows, changed, unexpected

    def _validate(self, value):
        soup = BeautifulSoup(value, 'html.parser')
        replaced = []
        for tag in soup.find_all(True):
            if tag.name == 'a':
                match = INTERNAL_LINK_HREF_RE.match(str(tag))
                if match:
                    old_tag = str(tag)
                    try:
                        if match.group('dossier_pk'):
                            obj = apps.get_model('dossiers', 'Dossier').objects.get(
                                pk=match.group('dossier_pk')
                            )
                        elif match.group('slug'):
                            obj = apps.get_model('dossiers', 'Dossier').objects.get(
                                slug=unquote(match.group('slug'))
                            )
                        elif match.group('individu_slug'):
                            obj = apps.get_model('libretto', 'Individu').objects.get(
                                slug=unquote(match.group('individu_slug'))
                            )
                        elif match.group('oeuvre_slug'):
                            obj = apps.get_model('libretto', 'Oeuvre').objects.get(
                                slug=unquote(match.group('oeuvre_slug'))
                            )
                        elif match.group('ensemble_slug'):
                            obj = apps.get_model('libretto', 'Ensemble').objects.get(
                                slug=unquote(match.group('ensemble_slug'))
                            )
                        elif match.group('lieu_slug'):
                            obj = apps.get_model('libretto', 'Lieu').objects.get(
                                slug=unquote(match.group('lieu_slug'))
                            )
                        elif match.group('profession_slug'):
                            obj = apps.get_model('libretto', 'Profession').objects.get(
                                slug=unquote(match.group('profession_slug'))
                            )
                        elif match.group('username'):
                            obj = apps.get_model(
                                'accounts', 'HierarchicUser'
                            ).objects.get(username=unquote(match.group('username')))
                        else:
                            app_label, model_name = INTERNAL_LINK_MODELS[
                                match.group('type')
                            ]
                            obj = apps.get_model(app_label, model_name).objects.get(
                                pk=match.group('pk')
                            )
                    except ObjectDoesNotExist:
                        raise UnexpectedTagError(
                            f'internal link target not found for tag {old_tag!r}'
                        )
                    if match.group('username'):
                        new_tag = format_html(
                            '<a href="{}">{}</a>',
                            DEZEDE_URL_PREFIX + obj.get_absolute_url(), tag.get_text(),
                        )
                    else:
                        new_tag = build_snippet_link_html(obj, tag.get_text())
                    tag.replace_with(BeautifulSoup(new_tag, 'html.parser'))
                    replaced.append((old_tag, new_tag))
                    continue
                href = tag.get('href')
                if href and self._is_strictly_external(href):
                    old_tag = str(tag)
                    if set(tag.attrs) != {'href'}:
                        tag.attrs = {'href': href}
                        replaced.append((old_tag, str(tag)))
                    continue
                if href and self._is_relative_internal(href):
                    old_tag = str(tag)
                    new_href = DEZEDE_URL_PREFIX + '/' + href.lstrip('./')
                    new_tag_ = format_html(
                        '<a href="{}">{}</a>', new_href, tag.get_text(),
                    )
                    tag.replace_with(BeautifulSoup(new_tag_, 'html.parser'))
                    replaced.append((old_tag, new_tag_))
                    continue
                raise UnexpectedTagError(f'unexpected tag {str(tag)!r}')
            if tag.name in ALLOWED_BARE_TAGS and not tag.attrs:
                continue
            if tag.attrs == ALLOWED_ATTRS.get(tag.name):
                continue
            if tag.name == 'p' and self._is_align(tag, 'center'):
                old_tag = str(tag)
                del tag['style']
                wrapper = soup.new_tag('align-center')
                tag.wrap(wrapper)
                replaced.append((old_tag, str(wrapper)))
                continue
            if tag.name == 'p' and self._is_align(tag, 'right'):
                old_tag = str(tag)
                del tag['style']
                tag.name = 'align-right'
                replaced.append((old_tag, str(tag)))
                continue
            if tag.name == 'p' and self._is_align(tag, 'left'):
                old_tag = str(tag)
                del tag['style']
                replaced.append((old_tag, str(tag)))
                continue
            if tag.name == 'p' and set(tag.attrs) == {'style'} and not tag['style'].strip():
                old_tag = str(tag)
                del tag['style']
                replaced.append((old_tag, str(tag)))
                continue
            if tag.name == 'span' and self._is_underline(tag):
                old_tag = str(tag)
                del tag['style']
                tag.name = 'u'
                replaced.append((old_tag, str(tag)))
                continue
            if tag.name == 'span' and self._is_strikethrough(tag):
                old_tag = str(tag)
                del tag['style']
                tag.name = 's'
                replaced.append((old_tag, str(tag)))
                continue
            if tag.name == 'span' and tag.attrs == {'class': ['bb_italic']}:
                old_tag = str(tag)
                del tag['class']
                tag.name = 'em'
                replaced.append((old_tag, str(tag)))
                continue
            if tag.name == 'span' and not any(tag.attrs.values()):
                old_tag = str(tag)
                tag.unwrap()
                replaced.append((old_tag, ''))
                continue
            raise UnexpectedTagError(f'unexpected tag {str(tag)!r}')
        return replaced, str(soup)

    def _is_align(self, tag, value):
        if set(tag.attrs) != {'style'}:
            return False
        declarations = {d.strip() for d in tag['style'].split(';') if d.strip()}
        return declarations in (
            {f'text-align:{value}'}, {f'text-align: {value}'}
        )

    def _is_strictly_external(self, href):
        parsed = urlparse(href)
        return bool(parsed.scheme) and not href.startswith(DEZEDE_URL_PREFIX)

    def _is_relative_internal(self, href):
        parsed = urlparse(href)
        return not parsed.scheme and href.startswith('../')

    def _is_underline(self, tag):
        if set(tag.attrs) != {'style'}:
            return False
        declarations = {d.strip() for d in tag['style'].split(';') if d.strip()}
        return declarations in (
            {'text-decoration:underline'}, {'text-decoration: underline'}
        )

    def _is_strikethrough(self, tag):
        if set(tag.attrs) != {'style'}:
            return False
        declarations = {d.strip() for d in tag['style'].split(';') if d.strip()}
        return declarations in (
            {'text-decoration:line-through'}, {'text-decoration: line-through'}
        )
