from django.db import migrations


# Creates only what is missing: dropping and recreating a configuration fails
# when an object depends on it, and production already has all of them.
CREATE = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_ts_dict
                   WHERE dictname = 'french_stem_including_stopwords' AND pg_ts_dict_is_visible(oid)) THEN
        CREATE TEXT SEARCH DICTIONARY french_stem_including_stopwords (
            TEMPLATE = snowball,
            Language = french
        );
    END IF;

    IF NOT EXISTS (SELECT FROM pg_ts_config
                   WHERE cfgname = 'french_unaccent_including_stopwords' AND pg_ts_config_is_visible(oid)) THEN
        CREATE TEXT SEARCH CONFIGURATION french_unaccent_including_stopwords (COPY = french);
        ALTER TEXT SEARCH CONFIGURATION french_unaccent_including_stopwords
            ALTER MAPPING FOR hword, hword_part, word
            WITH unaccent, french_stem_including_stopwords;
        ALTER TEXT SEARCH CONFIGURATION french_unaccent_including_stopwords
            ALTER MAPPING FOR asciihword, asciiword, hword_asciipart
            WITH french_stem_including_stopwords;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_ts_config
                   WHERE cfgname = 'simple_unaccent' AND pg_ts_config_is_visible(oid)) THEN
        CREATE TEXT SEARCH CONFIGURATION simple_unaccent (COPY = simple);
        ALTER TEXT SEARCH CONFIGURATION simple_unaccent
            ALTER MAPPING FOR hword, hword_part, word
            WITH unaccent, simple;
    END IF;
END
$$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('dezede', '0014_alter_diapositive_content_type'),
    ]

    operations = [
        migrations.RunSQL('CREATE EXTENSION IF NOT EXISTS unaccent', migrations.RunSQL.noop),
        migrations.RunSQL(CREATE, migrations.RunSQL.noop),
    ]
