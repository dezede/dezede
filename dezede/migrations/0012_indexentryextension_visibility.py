from django.db import connection, migrations, models


def backfill_visibility(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    quote = connection.ops.quote_name
    ext = quote('dezede_indexentryextension')
    entry = quote('wagtailsearch_indexentry')
    etat = quote(apps.get_model('libretto', 'Etat')._meta.db_table)
    for model in apps.get_models():
        local_names = {f.name for f in model._meta.local_fields}
        if not {'etat', 'owner'} <= local_names:
            continue
        try:
            content_type = ContentType.objects.get(
                app_label=model._meta.app_label, model=model._meta.model_name)
        except ContentType.DoesNotExist:
            continue
        schema_editor.execute(
            f"""
            UPDATE {ext} AS ext
            SET public = etat.public, owner_pk = obj.{quote(model._meta.get_field('owner').column)}
            FROM {entry} AS entry,
                 {quote(model._meta.db_table)} AS obj,
                 {etat} AS etat
            WHERE ext.index_entry_ptr_id = entry.id
              AND entry.content_type_id = %s
              AND entry.object_id = obj.{quote(model._meta.pk.column)}::text
              AND etat.id = obj.{quote(model._meta.get_field('etat').column)}
            """,
            [content_type.pk],
        )


def move_dossier_subclass_entries(apps, schema_editor):
    # Dossiers are now indexed under `Dossier` only. A dossier saved since the
    # last full reindex has no `Dossier` entry yet, so its subclass entry is
    # moved there instead of being dropped.
    ContentType = apps.get_model('contenttypes', 'ContentType')
    IndexEntry = apps.get_model('wagtailsearch', 'IndexEntry')
    dossier = ContentType.objects.filter(
        app_label='dossiers', model='dossier').first()
    if dossier is None:
        return
    subclass_entries = IndexEntry.objects.filter(
        content_type__app_label='dossiers',
        content_type__model__in=['dossierdevenements', 'dossierdoeuvres'],
    )
    subclass_entries.exclude(
        object_id__in=IndexEntry.objects.filter(
            content_type=dossier).values('object_id'),
    ).update(content_type=dossier)
    subclass_entries.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dezede', '0011_indexentryextension_alter_diapositive_content_type'),
        ('libretto', '0065_django_tree_binary_path'),
        ('dossiers', '0014_django_tree_binary_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='indexentryextension',
            name='public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='indexentryextension',
            name='owner_pk',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.RunPython(
            move_dossier_subclass_entries, migrations.RunPython.noop),
        migrations.RunPython(backfill_visibility, migrations.RunPython.noop),
    ]
