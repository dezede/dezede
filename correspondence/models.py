from django.db.models import ForeignKey, CASCADE, PROTECT, CharField, ManyToManyField
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel, InlinePanel, MultiFieldPanel, FieldRowPanel, MultipleChooserPanel,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.models import Page, Orderable
from wagtail.search.index import SearchField, RelatedFields

from correspondence.serializer_fields import RichTextSerializer
from libretto.models.base import SpaceTimeFields

from .blocks import ReferencesStreamBlock


class BasePage(Page):
    api_fields = [
        APIField('ancestors'),
    ]

    class Meta:
        abstract = True

    def ancestors(self):
        return [
            {'id': pk, 'title': title} for pk, title in self.get_ancestors().filter(
                depth__gt=1,
            ).values_list('pk', 'title')
        ]


class LetterIndex(BasePage):
    description = RichTextField(_('description'), blank=True)

    parent_page_types = ['wagtailcore.Page']
    max_count = 1
    content_panels = BasePage.content_panels + [
        FieldPanel('description'),
    ]

    class Meta:
        verbose_name = pgettext_lazy('singulier', 'index de lettres')
        verbose_name_plural = pgettext_lazy('pluriel', 'index de lettres')


class LetterCorpus(BasePage):
    person = ForeignKey(
        'libretto.Individu', on_delete=PROTECT, related_name='letter_corpuses',
        verbose_name=_('individu'),
    )
    description = RichTextField(_('description'), blank=True)

    parent_page_types = ['correspondence.LetterIndex']
    content_panels = BasePage.content_panels + [
        FieldPanel('person'),
        FieldPanel('description'),
    ]
    search_fields = [
        *BasePage.search_fields,
        SearchField('person', boost=10),
        SearchField('description'),
    ]
    api_fields = [
        *BasePage.api_fields,
        APIField('person'),
        APIField('description', serializer=RichTextSerializer()),
    ]

    class Meta:
        verbose_name = pgettext_lazy('singulier', 'corpus de lettres')
        verbose_name_plural = pgettext_lazy('pluriel', 'corpus de lettres')


class LetterRecipient(Orderable):
    letter = ParentalKey('correspondence.Letter', on_delete=CASCADE, related_name='recipients')
    person = ForeignKey(
        'libretto.Individu', on_delete=PROTECT, related_name='letter_recipients',
        verbose_name=_('individu'),
    )

    panels = [
        FieldPanel('person'),
    ]
    api_fields = [
        APIField('person'),
    ]

    class Meta(Orderable.Meta):
        verbose_name = _('destinataire')
        verbose_name_plural = _('destinataires')


class LetterImage(Orderable):
    letter = ParentalKey('correspondence.Letter', on_delete=CASCADE, related_name='letter_images')
    name = CharField(_('nom'), max_length=20, help_text=_('Exemple : « Page 1 » ou « Enveloppe »'))
    image = ForeignKey('wagtailimages.Image', on_delete=PROTECT, related_name='+', verbose_name=_('image'))
    references = StreamField(
        ReferencesStreamBlock, verbose_name=_('références'), use_json_field=True, blank=True,
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('image'),
        FieldPanel('references'),
    ]
    api_fields = [
        APIField('name'),
        APIField('image', serializer=ImageRenditionField('max-400x800')),
        APIField('thumbnail', serializer=ImageRenditionField('fill-100x100', source='image')),
        APIField('references'),
    ]

    class Meta(Orderable.Meta):
        verbose_name = _('image de lettre')
        verbose_name_plural = _('images de lettres')


class Letter(BasePage):
    sender = ForeignKey(
        'libretto.Individu', on_delete=PROTECT, related_name='sent_letters',
        verbose_name=_('expéditeur')
    )
    writing = SpaceTimeFields(verbose_name=_('rédaction'))

    transcription = RichTextField(_('transcription'), editor='transcription', blank=True)
    description = RichTextField(_('description'), blank=True)

    recipient_persons = ManyToManyField('libretto.Individu', through=LetterRecipient)

    parent_page_types = ['correspondence.LetterCorpus']
    content_panels = BasePage.content_panels + [
        FieldPanel('sender'),
        MultipleChooserPanel(
            'recipients', 'person', heading=_('Destinataires'), label=_('destinataire'),
        ),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('writing_lieu'), FieldPanel('writing_lieu_approx'),
            ]),
            FieldRowPanel([
                FieldPanel('writing_date'), FieldPanel('writing_date_approx'),
            ]),
            FieldRowPanel([
                FieldPanel('writing_heure'), FieldPanel('writing_heure_approx'),
            ]),
        ], heading=_('Rédaction')),
        InlinePanel('letter_images', heading=_('Images'), label=_('image')),
        FieldPanel('transcription'),
    ]
    search_fields = [
        *BasePage.search_fields,
        RelatedFields('sender', [
            SearchField('nom', boost=10),
        ]),
        RelatedFields('recipient_persons', [
            SearchField('nom'),
        ])
    ]
    api_fields = [
        *BasePage.api_fields,
        APIField('sender'),
        APIField('recipients'),
        APIField('writing_lieu'),
        APIField('writing_lieu_approx'),
        APIField('writing_date'),
        APIField('writing_date_approx'),
        APIField('letter_images'),
        APIField('transcription', serializer=RichTextSerializer()),
        APIField('description', serializer=RichTextSerializer()),
    ]

    class Meta:
        verbose_name = pgettext_lazy('correspondance épistolaire', 'lettre')
        verbose_name_plural = pgettext_lazy('correspondance épistolaire', 'lettres')
