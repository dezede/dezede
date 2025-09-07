from functools import cached_property
from bs4 import BeautifulSoup
from django.db.models import ForeignKey, CASCADE, PROTECT, CharField, ManyToManyField, URLField
from django.shortcuts import redirect
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
from dezede.constants import IMAGE_SPEC, THUMBNAIL_SPEC
from libretto.contants import INDIVIDU_SEARCH_FIELDS, LIEU_SEARCH_FIELDS
from libretto.models.base import SpaceTimeFields

from .blocks import BodyStreamBlock, ReferencesStreamBlock


Page.teaser_image = None
Page.api_fields = [
    APIField('teaser_thumbnail', serializer=ImageRenditionField(THUMBNAIL_SPEC, source='specific.teaser_image')),
]


class BasePageNoImage(Page):
    class Meta(Page.Meta):
        abstract = True

    def serve(self, request, *args, **kwargs):
        return redirect(f'/openletter{self.relative_url(None)}')


class BasePage(BasePageNoImage):
    teaser_image = ForeignKey(
        'wagtailimages.Image', on_delete=PROTECT, related_name='+', null=True, blank=True,
        verbose_name=_('image d’accroche'),
    )

    promote_panels = BasePageNoImage.promote_panels + [
        FieldPanel('teaser_image'),
    ]

    class Meta(Page.Meta):
        abstract = True


class LetterIndex(BasePage):
    body = StreamField(BodyStreamBlock(), blank=True, verbose_name=_('contenu'), use_json_field=True)

    parent_page_types = ['wagtailcore.Page']
    max_count = 1
    content_panels = BasePage.content_panels + [
        FieldPanel('body'),
    ]
    search_fields = [
        *BasePage.search_fields,
        SearchField('body'),
    ]
    api_fields = [
        *BasePage.api_fields,
        APIField('body'),
    ]

    class Meta(BasePage.Meta):
        verbose_name = pgettext_lazy('singulier', 'index de lettres')
        verbose_name_plural = pgettext_lazy('pluriel', 'index de lettres')


class LetterCorpus(BasePage):
    person = ForeignKey(
        'libretto.Individu', on_delete=PROTECT, related_name='letter_corpuses',
        verbose_name=_('individu'),
    )
    body = StreamField(BodyStreamBlock(), blank=True, verbose_name=_('contenu'), use_json_field=True)

    parent_page_types = ['correspondence.LetterIndex']
    content_panels = BasePage.content_panels + [
        FieldPanel('person'),
        FieldPanel('body'),
    ]
    search_fields = [
        *BasePage.search_fields,
        SearchField('person', boost=10),
        SearchField('body'),
    ]
    api_fields = [
        *BasePage.api_fields,
        APIField('person'),
        APIField('body'),
        APIField('total_count'),
        APIField('from_count'),
        APIField('to_count'),
    ]

    class Meta(BasePage.Meta):
        verbose_name = pgettext_lazy('singulier', 'corpus de lettres')
        verbose_name_plural = pgettext_lazy('pluriel', 'corpus de lettres')

    @cached_property
    def total_count(self) -> int:
        return Letter.objects.child_of(self).count()

    @cached_property
    def from_count(self) -> int:
        return Letter.objects.child_of(self).filter(sender=self.person).count()

    @cached_property
    def to_count(self) -> int:
        return Letter.objects.child_of(self).filter(recipient_persons=self.person).count()


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
    image = ForeignKey('wagtailimages.Image', on_delete=PROTECT, related_name='+', verbose_name=_('image'))
    name = CharField(_('nom'), max_length=20, help_text=_('Exemple : « Page 1 » ou « Enveloppe »'))
    references = StreamField(
        ReferencesStreamBlock, verbose_name=_('références'), use_json_field=True, blank=True,
    )

    panels = [
        FieldPanel('image'),
        FieldPanel('name'),
        FieldPanel('references'),
    ]
    api_fields = [
        APIField('name'),
        APIField('image', serializer=ImageRenditionField(IMAGE_SPEC)),
        APIField('thumbnail', serializer=ImageRenditionField(THUMBNAIL_SPEC, source='image')),
        APIField('references'),
    ]

    class Meta(Orderable.Meta):
        verbose_name = _('image de lettre')
        verbose_name_plural = _('images de lettres')


class Letter(BasePageNoImage):
    sender = ForeignKey(
        'libretto.Individu', on_delete=PROTECT, related_name='sent_letters',
        verbose_name=_('expéditeur')
    )
    writing = SpaceTimeFields(verbose_name=_('rédaction'))
    edition = CharField(_('édition'), max_length=50, blank=True)
    storage_place = ForeignKey(
        'libretto.Lieu', on_delete=PROTECT, related_name='stored_letters',
        verbose_name=_('lieu de conservation'), blank=True, null=True,
    )
    storage_call_number = CharField(_('cote'), max_length=60, blank=True)
    source_url = URLField(_('URL d’origine'), blank=True)

    transcription = RichTextField(_('transcription'), editor='transcription', blank=True)
    description = RichTextField(_('description'), blank=True)

    recipient_persons = ManyToManyField(
        'libretto.Individu', through=LetterRecipient, related_name='received_letters',
    )

    parent_page_types = ['correspondence.LetterCorpus']
    content_panels = BasePageNoImage.content_panels + [
        FieldPanel('sender'),
        MultipleChooserPanel(
            'recipients', 'person', heading=_('Destinataires'), label=_('destinataire'), max_num=10,
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
        FieldPanel('edition'),
        FieldRowPanel([
            FieldPanel('storage_place'),
            FieldPanel('storage_call_number'),
        ], heading=_('Conservation')),
        FieldPanel('source_url'),
        InlinePanel('letter_images', heading=_('Images'), label=_('image'), max_num=20),
        FieldPanel('transcription'),
        FieldPanel('description'),
    ]
    search_fields = [
        *BasePageNoImage.search_fields,
        RelatedFields('sender', [
            SearchField('nom', boost=10),
        ]),
        RelatedFields('recipient_persons', INDIVIDU_SEARCH_FIELDS),
        RelatedFields('writing_lieu', LIEU_SEARCH_FIELDS),
        SearchField('writing_lieu_approx'),
        SearchField('writing_date'),
        SearchField('writing_date_approx'),
        SearchField('transcription', boost=10),
        SearchField('description', boost=0.1),
    ]
    api_fields = [
        *BasePageNoImage.api_fields,
        APIField('sender'),
        APIField('recipients'),
        APIField('writing_lieu'),
        APIField('writing_lieu_approx'),
        APIField('writing_date'),
        APIField('writing_date_approx'),
        APIField('writing_heure'),
        APIField('writing_heure_approx'),
        APIField('edition'),
        APIField('storage_place'),
        APIField('storage_call_number'),
        APIField('source_url'),
        APIField('letter_images'),
        APIField('transcription', serializer=RichTextSerializer()),
        APIField('transcription_text'),
        APIField('description', serializer=RichTextSerializer()),
    ]

    class Meta(BasePageNoImage.Meta):
        verbose_name = pgettext_lazy('correspondance épistolaire', 'lettre')
        verbose_name_plural = pgettext_lazy('correspondance épistolaire', 'lettres')

    @property
    def transcription_text(self) -> str:
        return BeautifulSoup(self.transcription, 'html.parser').get_text(' ').strip()
