__version__ = 3, 5, 0
get_version = lambda: '.'.join(str(i) for i in __version__)

default_app_config = 'dezede.apps.DezedeConfig'

# Workaround to fix compatibility with recent libgeos versions.
import sys
try:
    import django.contrib.gis.geos.libgeos
except Exception as e:
    import re
    setattr(
        sys.modules['django.contrib.gis.geos.libgeos'], 'version_regex',
        re.compile(
            '^(?P<version>(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<subminor>\\d+))((rc(?P<release_candidate>\\d+))|dev)?-CAPI-(?P<capi_version>\\d+\\.\\d+\\.\\d+)( r\\d+)?( \\w+)?.*$'
        ),
    )
    assert str(type(e)) == "<class 'django.contrib.gis.geos.error.GEOSException'>", str(e)
