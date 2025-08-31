from django.utils.translation import gettext_lazy as _
from wagtail.blocks import StreamBlock
from wagtail.snippets.blocks import SnippetChooserBlock


class ReferencesStreamBlock(StreamBlock):
    lieu = SnippetChooserBlock('libretto.Lieu', label=_('Lieu ou institution'))
    individu = SnippetChooserBlock('libretto.Individu', label=_('Individu'))
    ensemble = SnippetChooserBlock('libretto.Ensemble', label=_('Ensemble'))
    oeuvre = SnippetChooserBlock('libretto.Oeuvre', label=_('Œuvre'))
    evenement = SnippetChooserBlock('libretto.Evenement', label=_('Événement'))
    partie = SnippetChooserBlock('libretto.Partie', label=_('Rôle ou instrument'))
