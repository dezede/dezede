# coding: utf-8

from __future__ import unicode_literals
from django.contrib.sites.models import get_current_site


def site(request):
    return {'SITE_URL': 'http://%s' % get_current_site(request)}
