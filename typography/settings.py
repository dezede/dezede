from django.conf import settings
from django.db.models.signals import pre_init, pre_save


__all__ = ('SIGNALS',)


SIGNALS = getattr(settings, 'TYPOGRAPHY_SIGNALS', {
    'pre_init': pre_init,
    'pre_save': pre_save,
})
