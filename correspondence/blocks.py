from wagtail.blocks import StreamBlock
from wagtail.snippets.blocks import SnippetChooserBlock


class ReferencesStreamBlock(StreamBlock):
    lieu = SnippetChooserBlock('libretto.Lieu')
    individu = SnippetChooserBlock('libretto.Individu')
    ensemble = SnippetChooserBlock('libretto.Ensemble')
    oeuvre = SnippetChooserBlock('libretto.Oeuvre')
    evenement = SnippetChooserBlock('libretto.Evenement')
    partie = SnippetChooserBlock('libretto.Partie')
