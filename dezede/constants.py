THUMBNAIL_SPEC = 'fill-200x200'
IMAGE_SPEC = 'max-1920x1080'

# The objects a slide can link to, by name of the form field that chooses them.
# These are the snippets, which have a chooser in the Wagtail admin.
LINKABLE_MODELS = {
    'objet_profession': 'libretto.profession',
    'objet_individu': 'libretto.individu',
    'objet_oeuvre': 'libretto.oeuvre',
    'objet_source': 'libretto.source',
    'objet_partie': 'libretto.partie',
    'objet_ensemble': 'libretto.ensemble',
    'objet_lieu': 'libretto.lieu',
    'objet_evenement': 'libretto.evenement',
    'objet_audio': 'libretto.audio',
    'objet_video': 'libretto.video',
    'objet_dossier': 'dossiers.dossier',
}
