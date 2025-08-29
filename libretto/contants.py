from wagtail.search.index import SearchField, RelatedFields


INDIVIDU_SEARCH_FIELDS = [
    SearchField('nom', boost=10), SearchField('nom_naissance'),
    SearchField('prenoms'), SearchField('pseudonyme', boost=10),
]
LIEU_SEARCH_FIELDS = [
    SearchField('nom', boost=10),
    RelatedFields('parent', [SearchField('nom')]),
    RelatedFields('nature', [SearchField('nom')])
]
