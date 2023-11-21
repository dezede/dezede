import re
from warnings import warn

from compressor.exceptions import UncompressableFileError
from django.apps import AppConfig
from django.conf import settings
from django.template import Template, Context


class DezedeConfig(AppConfig):
    name = 'dezede'
    verbose_name = 'Dezède'

    def ready(self):
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
