import re

from django.conf import settings
from django.core.exceptions import TooManyFieldsSent
from django.shortcuts import render
from django.template.response import TemplateResponse


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.MAINTENANCE_MODE:
            return self.get_response(request)

        if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
            return self.get_response(request)

        for url_pattern in settings.MAINTENANCE_IGNORE_URLS:
            if re.match(url_pattern, request.get_full_path()):
                return TemplateResponse(request, '503.html', status=503)

        return self.get_response(request)


class CorsHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
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
        return response


class MaxFieldsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            request.POST
        except TooManyFieldsSent:
            return render(request,'413.html', status=413)
        response = self.get_response(request)
        return response
