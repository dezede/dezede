from django.db import migrations

import tree.fields
import tree.operations


class Migration(migrations.Migration):
    """Upgrade ``django-tree`` 0.6.2 → 1.0.0 for ``Dossier``.

    See ``libretto.migrations.0065_django_tree_binary_path`` for the full
    rationale: the path column goes from ``numeric[]`` to ``bytea`` and every
    path is recomputed from the ``parent`` foreign keys and ``order_by`` columns.
    """

    dependencies = [
        ('dossiers',
         '0013_remove_categoriededossiers_categoriedossiers_search_and_more'),
        ('tree', '0003_tree_functions'),
    ]

    operations = [
        # 1. Drop the trigger and its numeric[] update_paths() function.
        tree.operations.DeleteTreeTrigger(model_lookup='dossier'),

        # 2. Drop the old numeric[] expression indexes before the type change.
        migrations.RemoveIndex(model_name='dossier', name='dossiers_path_parent_index'),
        migrations.RemoveIndex(model_name='dossier', name='dossiers_path_level_index'),
        migrations.RemoveIndex(model_name='dossier', name='dossiers_path_slice_1_index'),
        migrations.RemoveIndex(model_name='dossier', name='dossiers_path_slice_2_index'),
        migrations.RemoveIndex(model_name='dossier', name='dossiers_path_slice_3_index'),
        migrations.RemoveIndex(model_name='dossier', name='dossiers_path_slice_4_index'),
        migrations.RemoveIndex(model_name='dossier', name='dossiers_path_slice_5_index'),

        # 3. Convert the column to bytea (paths dropped, rebuilt at step 5).
        migrations.RunSQL(
            'ALTER TABLE dossiers_dossier ALTER COLUMN path TYPE bytea USING NULL',
            reverse_sql=migrations.RunSQL.noop,
        ),

        # 4. Add the new functional path index.
        migrations.AddIndex(
            model_name='dossier',
            index=tree.fields.PathIndex('path', name='dossiers_path_level_index'),
        ),

        # 5. Recreate the bytea trigger and recompute every path.
        tree.operations.CreateTreeTrigger(model_lookup='dossier'),
        tree.operations.RebuildPaths(model_lookup='dossier'),
    ]
