from functools import cached_property, wraps
from bs4 import BeautifulSoup
from django.db.models import ForeignKey, CASCADE, PROTECT, CharField, ManyToManyField, URLField
from django.http import Http404
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
from dezede.utils import richtext_to_text
from libretto.contants import INDIVIDU_SEARCH_FIELDS, LIEU_SEARCH_FIELDS
from libretto.models.base import SpaceTimeFields

from .blocks import BodyStreamBlock


original_get_url_parts = Page.get_url_parts


class PageMonkeyPatching(Page):
    class Meta(Page.Meta):
        abstract = True

    @wraps(original_get_url_parts)
    def get_url_parts(self, request=None):
        url_parts = original_get_url_parts(self, request)
        if url_parts is None:
            return None
        site_id, root_url, page_path = url_parts
        if page_path is None:
            return url_parts
        return site_id, root_url, f'/openletter{page_path}'


Page.get_url_parts = PageMonkeyPatching.get_url_parts


Page.teaser_image = None
Page.api_fields = [
    APIField('teaser_thumbnail', serializer=ImageRenditionField(THUMBNAIL_SPEC, source='specific.teaser_image')),
]
Page.show_in_menus_default = True


class BasePageNoImage(Page):
    class Meta(Page.Meta):
        abstract = True

    # FIXME: Make preview_modes compatible with Next.js
    #        instead of disabling it.
    @property
    def preview_modes(self):
        return []

    def serve_preview(self, request, mode_name):
        raise Http404


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
        return Letter.objects.child_of(self).filter(sender_persons=self.person).count()

    @cached_property
    def to_count(self) -> int:
        return Letter.objects.child_of(self).filter(recipient_persons=self.person).count()


class LetterSender(Orderable):
    letter = ParentalKey('correspondence.Letter', on_delete=CASCADE, related_name='senders')
    person = ForeignKey(
        'libretto.Individu', on_delete=PROTECT, related_name='letter_senders',
        verbose_name=_('individu'),
    )

    panels = [
        FieldPanel('person'),
    ]
    api_fields = [
        APIField('person'),
    ]

    class Meta(Orderable.Meta):
        verbose_name = _('expéditeur')
        verbose_name_plural = _('expéditeurs')


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

    panels = [
        FieldPanel('image'),
        FieldPanel('name'),
    ]
    api_fields = [
        APIField('name'),
        APIField('image', serializer=ImageRenditionField(IMAGE_SPEC)),
        APIField('thumbnail', serializer=ImageRenditionField(THUMBNAIL_SPEC, source='image')),
    ]

    class Meta(Orderable.Meta):
        verbose_name = _('image de lettre')
        verbose_name_plural = _('images de lettres')


class Letter(BasePageNoImage):
    writing = SpaceTimeFields(verbose_name=_('rédaction'), for_wagtail=True)
    edition = CharField(_('édition'), max_length=50, blank=True)
    storage_place = ForeignKey(
        'libretto.Lieu', on_delete=PROTECT, related_name='stored_letters',
        verbose_name=_('lieu de conservation'), blank=True, null=True,
    )
    storage_call_number = CharField(_('cote'), max_length=60, blank=True)
    source_url = URLField(_('URL d’origine'), blank=True)

    transcription = RichTextField(_('transcription'), editor='transcription', blank=True)
    description = RichTextField(_('description'), blank=True)

    sender_persons = ManyToManyField(
        'libretto.Individu', through=LetterSender, related_name='sent_letters',
    )

    recipient_persons = ManyToManyField(
        'libretto.Individu', through=LetterRecipient, related_name='received_letters',
    )

    parent_page_types = ['correspondence.LetterCorpus']
    content_panels = BasePageNoImage.content_panels + [
        MultipleChooserPanel(
            'senders', 'person', heading=_('Expéditeurs'), label=_('expéditeur'), min_num=1, max_num=10,
        ),
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
        RelatedFields('sender_persons', INDIVIDU_SEARCH_FIELDS),
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
        APIField('senders'),
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
        return richtext_to_text(self.transcription)
