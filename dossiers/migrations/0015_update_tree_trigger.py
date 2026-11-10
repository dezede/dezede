from django.db import migrations

from tree.operations import UpdateTreeTrigger


class Migration(migrations.Migration):
    """Upgrade ``django-tree`` 1.0.1 → 1.1.0 (faster PostgreSQL triggers)."""

    dependencies = [
        ('tree', '0003_tree_functions'),
        ('dossiers', '0014_django_tree_binary_path'),
    ]

    operations = [
        UpdateTreeTrigger('dossier'),
    ]
