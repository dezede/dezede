from django.utils.translation import gettext_lazy as _
from wagtail.blocks import StreamBlock
from wagtail.snippets.blocks import SnippetChooserBlock


class PrefetchedChooserBlock(SnippetChooserBlock):
    def bulk_to_python(self, values):
        qs = self.model_class.objects
        if hasattr(self.meta, 'select_related'):
            qs = qs.select_related(*self.meta.select_related)
        if hasattr(self.meta, 'prefetch_related'):
            qs = qs.prefetch_related(*self.meta.prefetch_related)
        objects = qs.in_bulk(values)
        return [
            objects.get(id) for id in values
        ]  # Keeps the ordering the same as in values.


class ReferencesStreamBlock(StreamBlock):
    lieu = PrefetchedChooserBlock(
        'libretto.Lieu', label=_('Lieu ou institution'), select_related=['nature', 'parent'],
    )
    individu = SnippetChooserBlock('libretto.Individu', label=_('Individu'))
    ensemble = SnippetChooserBlock('libretto.Ensemble', label=_('Ensemble'))
    oeuvre = PrefetchedChooserBlock(
        'libretto.Oeuvre', label=_('Œuvre'),
        prefetch_related=['pupitres__partie__oeuvre'], select_related=['genre'],
    )
    evenement = PrefetchedChooserBlock(
        'libretto.Evenement', label=_('Événement'),
        select_related=['debut_lieu__parent', 'debut_lieu__nature'],
    )
    partie = PrefetchedChooserBlock(
        'libretto.Partie', label=_('Rôle ou instrument'),
        select_related=['oeuvre'],
    )
