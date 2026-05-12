from wagtail.search.index import AutocompleteField, SearchField, RelatedFields


INDIVIDU_RELATED_SEARCH_FIELDS = [
    SearchField('title'),
    SearchField('prenoms_complets'),
    AutocompleteField('title'),
    AutocompleteField('prenoms_complets'),
]
ENSEMBLE_RELATED_SEARCH_FIELDS = [
    SearchField('title'),
    AutocompleteField('title'),
]
LIEU_RELATED_SEARCH_FIELDS = [
    SearchField('title'),
    RelatedFields('parent', [
        SearchField('title'),
        AutocompleteField('title'),
    ]),
    RelatedFields('nature', [
        SearchField('title'),
        AutocompleteField('title'),
    ]),
    AutocompleteField('title'),
]
PROFESSION_RELATED_SEARCH_FIELDS = [
    SearchField('title'),
    SearchField('nom_pluriel'),
    SearchField('nom_feminin'),
    AutocompleteField('title'),
    AutocompleteField('nom_pluriel'),
    AutocompleteField('nom_feminin'),
]
PARTIE_RELATED_SEARCH_FIELDS = [
    SearchField('title'),
    SearchField('nom_pluriel'),
    AutocompleteField('title'),
    AutocompleteField('nom_pluriel'),
]
OEUVRE_RELATED_SEARCH_FIELDS = [
    SearchField('title', boost=10),
    RelatedFields('auteurs', [
        RelatedFields('individu', INDIVIDU_RELATED_SEARCH_FIELDS),
        RelatedFields('ensemble', ENSEMBLE_RELATED_SEARCH_FIELDS),
    ]),
    RelatedFields('genre', [
        SearchField('title'),
        SearchField('nom_pluriel'),
    ]),
    RelatedFields('pupitres', [
        RelatedFields('partie', PARTIE_RELATED_SEARCH_FIELDS),
    ]),
    AutocompleteField('title'),
]
SOURCE_RELATED_SEARCH_FIELDS = [
    RelatedFields('type', [
        SearchField('title'),
        SearchField('nom_pluriel'),
    ]),
    SearchField('title'),
]
DISTRIBUTION_SEARCH_FIELDS = [
    RelatedFields('individu', INDIVIDU_RELATED_SEARCH_FIELDS),
    RelatedFields('ensemble', ENSEMBLE_RELATED_SEARCH_FIELDS),
    RelatedFields('partie', PARTIE_RELATED_SEARCH_FIELDS),
    RelatedFields('profession', PROFESSION_RELATED_SEARCH_FIELDS),
]
CARACTERISTIQUES_PROGRAMME_SEARCH_FIELDS = [
    SearchField('title'),
    AutocompleteField('title'),
]
PROGRAMME_SEARCH_FIELDS = [
    RelatedFields('distribution', DISTRIBUTION_SEARCH_FIELDS),
    RelatedFields('oeuvre', OEUVRE_RELATED_SEARCH_FIELDS),
    SearchField('autre'),
    RelatedFields('caracteristiques', CARACTERISTIQUES_PROGRAMME_SEARCH_FIELDS),
]
