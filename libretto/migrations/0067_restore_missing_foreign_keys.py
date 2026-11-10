from django.db import migrations


FOREIGN_KEYS = (
    ('Membre', 'instrument'),
    ('ParenteDIndividus', 'type'),
    ('ParenteDOeuvres', 'type'),
)


def restore_foreign_keys(apps, schema_editor):
    # Production and databases built from the migrations both lack these
    # constraints: the old migrations that replaced the referenced models
    # dropped them. Skip any that already exist.
    for model_name, field_name in FOREIGN_KEYS:
        model = apps.get_model('libretto', model_name)
        field = model._meta.get_field(field_name)
        with schema_editor.connection.cursor() as cursor:
            constraints = schema_editor.connection.introspection.get_constraints(
                cursor, model._meta.db_table)
        if not any(c['foreign_key'] and c['columns'] == [field.column]
                   for c in constraints.values()):
            schema_editor.execute(schema_editor._create_fk_sql(
                model, field, '_fk_%(to_table)s_%(to_column)s'))


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0066_update_tree_trigger'),
    ]

    operations = [
        migrations.RunPython(restore_foreign_keys, migrations.RunPython.noop),
    ]
