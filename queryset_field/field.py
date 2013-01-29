# coding, utf-8

from __future__ import unicode_literals
from django.utils.translation import ungettext_lazy as _


operators = (
    ('exact', _('Exact')),
    ('iexact', _('Exact (case insensitive)')),
    ('contains', _('Contains')),
    ('icontains', _('Contains (case insensitive)')),
    ('regex', _('Regular expression')),
    ('iregex', _('Regular expression (case insensitive)')),
    ('gt', _('Greater than')),
    ('gte', _('Greater than or equal')),
    ('lt', _('Less than')),
    ('lte', _('Less than or equal')),
    ('startswith', _('Starts with')),
    ('endswith', _('Ends with')),
    ('istartswith', _('Starts with (case insensitive)')),
    ('iendswith', _('Ends with (case insensitive)')),
)
