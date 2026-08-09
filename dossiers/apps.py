from django.apps import AppConfig
import reversion


class DossiersConfig(AppConfig):
    name = 'dossiers'
    verbose_name = 'Dossiers'

    def ready(self):
        # ``Dossier`` used to be registered with django-reversion only as a
        # side effect of ``DossierAdmin`` inheriting ``VersionAdmin``, which
        # auto-registers on instantiation. The Django admin is on its way out,
        # and ``Dossier.convert_to_static()`` / ``convert_to_dynamic()`` record
        # a revision from the model layer — where no admin has necessarily been
        # loaded. An unregistered model makes ``reversion.create_revision()`` a
        # silent no-op rather than an error, so the conversions would quietly
        # stop being versioned the day ``dossiers/admin.py`` is deleted.
        # Registering here keeps that from happening; ``VersionAdmin``'s own
        # autoregistration skips models that are already registered, so the two
        # coexist until the admin goes.
        from .models import Dossier

        reversion.register(Dossier)
