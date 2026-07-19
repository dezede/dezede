from django.db import migrations

import tree.fields
import tree.operations


class Migration(migrations.Migration):
    """Upgrade ``django-tree`` 0.6.2 → 1.0.0.

    In 1.0.0 a tree path is no longer an array of decimals (``numeric[]``) but a
    single compact binary key (``bytea``), so ``PathField`` is now a
    ``BinaryField`` subclass. Because ``PathField`` keeps the same import path,
    the historical state already deconstructs to the new ``BinaryField`` flavour
    — Django therefore sees no field change and never tries to cast the column
    (there is no automatic ``numeric[]`` → ``bytea`` conversion anyway).

    The physical column must thus be converted by hand, and every path
    recomputed from scratch:

    1. drop the old triggers (they reference the ``numeric[]`` update function);
    2. drop the old ``numeric[]`` expression indexes (``__level`` /  ``__0_n``
       slices / parent index) — they cannot survive the column type change;
    3. convert each column to ``bytea`` (values dropped, rebuilt below);
    4. add the new functional ``PathIndex`` (``(level, path)`` on PostgreSQL);
    5. recreate the triggers (now ``bytea``-based) and rebuild every path from
       the ``parent`` / ``extrait_de`` foreign keys and the ``order_by`` columns.
    """

    dependencies = [
        ('libretto',
         '0064_remove_caracteristiquedeprogramme_caracdeprogramme_search_and_more'),
        # Provides the new bytea path SQL helpers (tree_level(), …).
        ('tree', '0003_tree_functions'),
    ]

    operations = [
        # 1. Drop the triggers and their numeric[] update_paths() functions.
        tree.operations.DeleteTreeTrigger(model_lookup='lieu'),
        tree.operations.DeleteTreeTrigger(model_lookup='oeuvre'),

        # 2. Drop the old numeric[] expression indexes. They are built on array
        #    operations that no longer make sense on a bytea column, so they must
        #    go before the type change.
        migrations.RemoveIndex(model_name='lieu', name='lieu_path_parent_index'),
        migrations.RemoveIndex(model_name='lieu', name='lieu_path_level_index'),
        migrations.RemoveIndex(model_name='lieu', name='lieu_path_slice_1_index'),
        migrations.RemoveIndex(model_name='lieu', name='lieu_path_slice_2_index'),
        migrations.RemoveIndex(model_name='lieu', name='lieu_path_slice_3_index'),
        migrations.RemoveIndex(model_name='lieu', name='lieu_path_slice_4_index'),
        migrations.RemoveIndex(model_name='lieu', name='lieu_path_slice_5_index'),
        migrations.RemoveIndex(model_name='oeuvre', name='oeuvre_path_parent_index'),
        migrations.RemoveIndex(model_name='oeuvre', name='oeuvre_path_level_index'),
        migrations.RemoveIndex(model_name='oeuvre', name='oeuvre_path_slice_1_index'),
        migrations.RemoveIndex(model_name='oeuvre', name='oeuvre_path_slice_2_index'),
        migrations.RemoveIndex(model_name='oeuvre', name='oeuvre_path_slice_3_index'),
        migrations.RemoveIndex(model_name='oeuvre', name='oeuvre_path_slice_4_index'),
        migrations.RemoveIndex(model_name='oeuvre', name='oeuvre_path_slice_5_index'),

        # 3. Convert the columns from numeric[] to bytea. There is no meaningful
        #    cast, so every path is dropped (set to NULL) and rebuilt at step 5.
        migrations.RunSQL(
            'ALTER TABLE libretto_lieu ALTER COLUMN path TYPE bytea USING NULL',
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            'ALTER TABLE libretto_oeuvre ALTER COLUMN path TYPE bytea USING NULL',
            reverse_sql=migrations.RunSQL.noop,
        ),

        # 4. Add the new functional path index.
        migrations.AddIndex(
            model_name='lieu',
            index=tree.fields.PathIndex('path', name='lieu_path_level_index'),
        ),
        migrations.AddIndex(
            model_name='oeuvre',
            index=tree.fields.PathIndex('path', name='oeuvre_path_level_index'),
        ),

        # 5. Recreate the bytea triggers and recompute every path.
        tree.operations.CreateTreeTrigger(model_lookup='lieu'),
        tree.operations.RebuildPaths(model_lookup='lieu'),
        tree.operations.CreateTreeTrigger(model_lookup='oeuvre'),
        tree.operations.RebuildPaths(model_lookup='oeuvre'),
    ]
