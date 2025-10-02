from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class NonStrictManifestStaticFilesStorage(ManifestStaticFilesStorage):
    manifest_strict = False
    # Prevents Django from trying to collect JS source map files.
    # This is critical because we don't have them all, and Django fails to collectstatic
    # when we miss one.
    patterns = []
