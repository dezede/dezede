from django.db import migrations


def restore_foreign_key(apps, schema_editor):
    # Production lacks this constraint, but a database built from the
    # migrations has it. Skip it when it already exists.
    model = apps.get_model('account', 'EmailAddress')
    field = model._meta.get_field('user')
    with schema_editor.connection.cursor() as cursor:
        constraints = schema_editor.connection.introspection.get_constraints(
            cursor, model._meta.db_table)
    if not any(c['foreign_key'] and c['columns'] == [field.column]
               for c in constraints.values()):
        schema_editor.execute(schema_editor._create_fk_sql(
            model, field, '_fk_%(to_table)s_%(to_column)s'))


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_update_tree_trigger'),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(restore_foreign_key, migrations.RunPython.noop),
    ]
