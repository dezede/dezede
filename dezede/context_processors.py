from urllib.parse import urljoin
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest


def get_absolute_url(relative_url: str = ''):
    return urljoin(settings.BASE_URL, relative_url)


def site(request: HttpRequest):
    return {
        'SITE': get_current_site(request),
        'BASE_URL': settings.BASE_URL,
        'absolute_url': get_absolute_url(request.get_full_path()),
    }
