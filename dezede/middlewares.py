import re
import time

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


class CorsHeadersMiddleware:
    def process_response(self, request, response):
        start_time = time.time()
        total = time.time() - start_time
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = (
            'POST, GET, PUT, PATCH, DELETE, OPTIONS'
        )
        response['Access-Control-Allow-Headers'] = (
            'Origin, X-Requested-With, Content-Type, Accept, Authorization'
        )
        response['Access-Control-Expose-Headers'] = (
            'Cache-Control, Content-Language, Content-Type, Expires, '
            'Last-Modified, Pragma, Set-Cookie'
        )
        response["X-Request-Generation-Duration-ms"] = int(total * 1000)
        return response
