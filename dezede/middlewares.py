from ipaddress import IPv6Address, ip_address
import re
from subprocess import check_output

from django.conf import settings
from django.core.exceptions import PermissionDenied, TooManyFieldsSent
from django.core.handlers.exception import get_exception_response
from django.http import HttpRequest
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import get_resolver, get_urlconf


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


def get_client_ip(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META['REMOTE_ADDR']


class CountryBlockMiddleware:
    pattern = re.compile(r'^GeoIP Country(?: V6)? Edition: ([A-Z]{2}), .+$')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            return None
        if request.resolver_match.url_name == 'account_login' or 'admin' in request.resolver_match.namespaces:
            return None
        ip = get_client_ip(request)
        command = 'geoiplookup'
        if isinstance(ip_address(ip), IPv6Address):
            command = 'geoiplookup6'
        match = self.pattern.match(check_output([command, ip]).decode().strip())
        if match is not None:
            country_code = match.group(1)
            if country_code in settings.BLOCKED_COUNTRIES:
                return render(request, "429.html", status=429)

        return None
