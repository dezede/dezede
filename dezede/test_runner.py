from django.contrib.contenttypes.models import ContentType
from django.test.runner import DiscoverRunner


class ContentTypeCacheRunner(DiscoverRunner):
    """Empties the content type cache once the test database exists.

    Wagtail registers the snippets at startup, which loads their content types
    from the development database. `migrate` only clears the cache of its own
    historical `ContentType`, so the real cache would keep those ids and the
    test database would reject them.
    """

    def setup_databases(self, **kwargs):
        config = super().setup_databases(**kwargs)
        ContentType.objects.clear_cache()
        return config
