# coding: utf-8

"""utils to help rename apps and South migrations"""

from __future__ import unicode_literals
import os
from south.models import MigrationHistory


def was_applied(migration_file_path, app_name):
    """true if migration with a given file name ``migration_file``
    was applied to app with name ``app_name``"""

    migration_file = os.path.basename(migration_file_path)
    migration_name = migration_file.split('.')[0]
    try:
        MigrationHistory.objects.get(
            app_name=app_name,
            migration=migration_name
        )
        return True
    except MigrationHistory.DoesNotExist:
        return False
