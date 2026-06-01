from wagtail.search.index import SearchField, RelatedFields


INDIVIDU_RELATED_SEARCH_FIELDS = [
    SearchField('title'),
    SearchField('prenoms_complets'),
]
ENSEMBLE_RELATED_SEARCH_FIELDS = [
    SearchField('title'),
]
LIEU_RELATED_SEARCH_FIELDS = [
    SearchField('title'),
    RelatedFields('parent', [
        SearchField('title'),
    ]),
    RelatedFields('nature', [
        SearchField('title'),
    ]),
]
PROFESSION_RELATED_SEARCH_FIELDS = [
    SearchField('title'),
    SearchField('nom_pluriel'),
    SearchField('nom_feminin'),
]
PARTIE_RELATED_SEARCH_FIELDS = [
    SearchField('title'),
    SearchField('nom_pluriel'),
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
]
PROGRAMME_SEARCH_FIELDS = [
    RelatedFields('distribution', DISTRIBUTION_SEARCH_FIELDS),
    RelatedFields('oeuvre', OEUVRE_RELATED_SEARCH_FIELDS),
    SearchField('autre'),
    RelatedFields('caracteristiques', CARACTERISTIQUES_PROGRAMME_SEARCH_FIELDS),
]
