import re
from warnings import warn

from compressor.exceptions import UncompressableFileError
from django.apps import AppConfig
from django.conf import settings
from django.template import Template, Context


def _patch_debug_toolbar_sql_panel():
    """sqlparse chokes on giant statements such as the fused dossier count
    batches: prettifying them takes seconds and its 10000-token guard raises
    SQLParseError, breaking every request the SQL panel instruments.  Shows
    them escaped and truncated instead."""
    from html import escape

    from debug_toolbar.panels.sql import utils
    from sqlparse.exceptions import SQLParseError

    original_parse_sql = utils.parse_sql

    def parse_sql(sql, *, simplify=False):
        if len(sql) > 20_000:
            return escape(sql[:20_000], quote=False) + ' […]'
        try:
            return original_parse_sql(sql, simplify=simplify)
        except SQLParseError:
            return escape(sql, quote=False)

    utils.parse_sql = parse_sql


class DezedeConfig(AppConfig):
    name = 'dezede'
    verbose_name = 'Dezède'

    def ready(self):
        if settings.DEBUG:
            _patch_debug_toolbar_sql_panel()
        # Sets TinyMCE styling to the front-end styling
        html = ('{% load compress static %}'
                '{% compress css %}'
                '  <link rel="stylesheet" type="text/less"'
                '        href="{% static "css/styles.less" %}" />'
                '{% endcompress %}')
        try:
            html = Template(html).render(Context())
        except (UncompressableFileError, ValueError):
            warn('Unable to apply front-end styling to the admin!')
        else:
            settings.TINYMCE_DEFAULT_CONFIG['content_css'] = re.search(
                r'href="([^"]+)"', html).group(1)
