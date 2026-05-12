from wagtail.search.index import AutocompleteField, SearchField, RelatedFields


INDIVIDU_RELATED_SEARCH_FIELDS = [
    SearchField('calc_titre'),
    SearchField('particule_nom'),
    SearchField('nom'),
    SearchField('particule_nom_naissance'),
    SearchField('nom_naissance'),
    SearchField('pseudonyme'),
    SearchField('prenoms'),
    AutocompleteField('calc_titre'),
    AutocompleteField('particule_nom'),
    AutocompleteField('nom'),
    AutocompleteField('particule_nom_naissance'),
    AutocompleteField('nom_naissance'),
    AutocompleteField('pseudonyme'),
    AutocompleteField('prenoms'),
    AutocompleteField('prenoms_complets'),
]
ENSEMBLE_RELATED_SEARCH_FIELDS = [
    SearchField('particule_nom'),
    SearchField('nom'),
    AutocompleteField('particule_nom'),
    AutocompleteField('nom'),
]
LIEU_RELATED_SEARCH_FIELDS = [
    SearchField('nom'),
    RelatedFields('parent', [
        SearchField('nom'),
        AutocompleteField('nom'),
    ]),
    RelatedFields('nature', [
        SearchField('nom'),
        AutocompleteField('nom'),
    ]),
    AutocompleteField('nom'),
]
PROFESSION_RELATED_SEARCH_FIELDS = [
    SearchField('nom'),
    SearchField('nom_pluriel'),
    SearchField('nom_feminin'),
    AutocompleteField('nom'),
    AutocompleteField('nom_pluriel'),
    AutocompleteField('nom_feminin'),
]
PARTIE_RELATED_SEARCH_FIELDS = [
    SearchField('nom'),
    SearchField('nom_pluriel'),
    AutocompleteField('nom'),
    AutocompleteField('nom_pluriel'),
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
    AutocompleteField('prefixe_titre'),
    AutocompleteField('titre'),
    AutocompleteField('prefixe_titre_secondaire'),
    AutocompleteField('titre_secondaire'),
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
    AutocompleteField('valeur'),
]
PROGRAMME_SEARCH_FIELDS = [
    RelatedFields('distribution', DISTRIBUTION_SEARCH_FIELDS),
    RelatedFields('oeuvre', OEUVRE_RELATED_SEARCH_FIELDS),
    SearchField('autre'),
    RelatedFields('caracteristiques', CARACTERISTIQUES_PROGRAMME_SEARCH_FIELDS),
]
