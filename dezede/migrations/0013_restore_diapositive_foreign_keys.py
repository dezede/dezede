from django.db import migrations


def restore_foreign_keys(apps, schema_editor):
    # The production table lacks these two constraints, but a database built
    # from the migrations has them. Skip any that already exist.
    model = apps.get_model('dezede', 'Diapositive')
    with schema_editor.connection.cursor() as cursor:
        constraints = schema_editor.connection.introspection.get_constraints(
            cursor, model._meta.db_table)
    existing = {tuple(c['columns']) for c in constraints.values()
                if c['foreign_key']}
    for name in ('etat', 'owner'):
        field = model._meta.get_field(name)
        if (field.column,) not in existing:
            schema_editor.execute(schema_editor._create_fk_sql(
                model, field, '_fk_%(to_table)s_%(to_column)s'))


class Migration(migrations.Migration):

    dependencies = [
        ('dezede', '0012_indexentryextension_visibility'),
    ]

    operations = [
        migrations.RunPython(restore_foreign_keys, migrations.RunPython.noop),
    ]
