# coding: utf-8

from __future__ import unicode_literals
import re
from django.conf import settings
from django.template.response import TemplateResponse


class MaintenanceModeMiddleware(object):
    def process_request(self, request):
        if not settings.MAINTENANCE_MODE:
            return

        if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
            return

        for url_pattern in settings.MAINTENANCE_IGNORE_URLS:
            if re.match(url_pattern, request.get_full_path()):
                return TemplateResponse(request, '503.html', status=503)
