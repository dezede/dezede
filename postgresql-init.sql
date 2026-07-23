-- Creates the unaccent extension and full-text search configurations that Django
-- migrations depend on.

CREATE EXTENSION IF NOT EXISTS unaccent;

DROP TEXT SEARCH CONFIGURATION IF EXISTS simple_unaccent;
DROP TEXT SEARCH CONFIGURATION IF EXISTS french_unaccent_including_stopwords;
DROP TEXT SEARCH DICTIONARY IF EXISTS french_stem_including_stopwords;

CREATE TEXT SEARCH DICTIONARY french_stem_including_stopwords (
    TEMPLATE = snowball,
    Language = french
);
CREATE TEXT SEARCH CONFIGURATION french_unaccent_including_stopwords (COPY = french);
ALTER TEXT SEARCH CONFIGURATION french_unaccent_including_stopwords
    ALTER MAPPING FOR hword, hword_part, word
    WITH unaccent, french_stem_including_stopwords;
ALTER TEXT SEARCH CONFIGURATION french_unaccent_including_stopwords
    ALTER MAPPING FOR asciihword, asciiword, hword_asciipart
    WITH french_stem_including_stopwords;

CREATE TEXT SEARCH CONFIGURATION simple_unaccent (COPY = simple);
ALTER TEXT SEARCH CONFIGURATION simple_unaccent
    ALTER MAPPING FOR hword, hword_part, word
    WITH unaccent, simple;
