from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dezede', '0009_remove_diapositive_diapositive_search_and_more'),
        ('wagtailsearch', '0009_remove_ngram_autocomplete'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX indexentry_gin_search ON wagtailsearch_indexentry USING GIN((title || body))",
            "DROP INDEX indexentry_gin_search",
        ),
    ]
