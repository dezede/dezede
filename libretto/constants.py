from wagtail.search.index import SearchField, RelatedFields


INDIVIDU_RELATED_SEARCH_FIELDS = [
    SearchField('calc_titre'),
    SearchField('particule_nom'),
    SearchField('nom'),
    SearchField('particule_nom_naissance'),
    SearchField('nom_naissance'),
    SearchField('pseudonyme'),
    SearchField('prenoms'),
]
ENSEMBLE_RELATED_SEARCH_FIELDS = [
    SearchField('particule_nom'),
    SearchField('nom'),
]
LIEU_RELATED_SEARCH_FIELDS = [
    SearchField('nom'),
    RelatedFields('parent', [SearchField('nom')]),
    RelatedFields('nature', [SearchField('nom')]),
]
PROFESSION_RELATED_SEARCH_FIELDS = [
    SearchField('nom'),
    SearchField('nom_pluriel'),
    SearchField('feminin'),
]
PARTIE_RELATED_SEARCH_FIELDS = [
    SearchField('nom'),
    SearchField('nom_pluriel'),
]
OEUVRE_RELATED_SEARCH_FIELDS = [
    SearchField('prefixe_titre'),
    SearchField('titre', boost=10),
    SearchField('prefixe_titre_secondaire'),
    SearchField('titre_secondaire', boost=2),
    SearchField('numero'),
    SearchField('coupe'),
    SearchField('tempo'),
    SearchField('get_tonalite_display'),
    SearchField('sujet'),
    SearchField('surnom', boost=10),
    SearchField('nom_courant', boost=10),
    SearchField('incipit', boost=10),
    SearchField('opus', boost=10),
    SearchField('ict', boost=10),
    SearchField('get_extrait'),
    RelatedFields('auteurs', [
        RelatedFields('individu', INDIVIDU_RELATED_SEARCH_FIELDS),
        RelatedFields('ensemble', ENSEMBLE_RELATED_SEARCH_FIELDS),
    ]),
    RelatedFields('genre', [
        SearchField('nom'),
        SearchField('nom_pluriel'),
    ]),
    RelatedFields('pupitres', [
        RelatedFields('partie', PARTIE_RELATED_SEARCH_FIELDS),
    ]),
]
SOURCE_RELATED_SEARCH_FIELDS = [
    RelatedFields('type', [
        SearchField('nom'),
        SearchField('nom_pluriel'),
    ]),
    SearchField('titre'),
    SearchField('date'),
    SearchField('date_approx'),
    SearchField('numero'),
    SearchField('lieu_conservation'),
    SearchField('cote'),
]
DISTRIBUTION_SEARCH_FIELDS = [
    RelatedFields('individu', INDIVIDU_RELATED_SEARCH_FIELDS),
    RelatedFields('ensemble', ENSEMBLE_RELATED_SEARCH_FIELDS),
    RelatedFields('partie', PARTIE_RELATED_SEARCH_FIELDS),
    RelatedFields('profession', PROFESSION_RELATED_SEARCH_FIELDS),
]
CARACTERISTIQUES_PROGRAMME_SEARCH_FIELDS = [
    SearchField('valeur'),
]
PROGRAMME_SEARCH_FIELDS = [
    RelatedFields('distribution', DISTRIBUTION_SEARCH_FIELDS),
    RelatedFields('oeuvre', OEUVRE_RELATED_SEARCH_FIELDS),
    SearchField('autre'),
    RelatedFields('caracteristiques', CARACTERISTIQUES_PROGRAMME_SEARCH_FIELDS),
]
