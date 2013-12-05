# coding: utf-8

from __future__ import unicode_literals, division
from decimal import Decimal
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    CharField, ImageField, DecimalField, BooleanField, ForeignKey,
    PositiveIntegerField, PositiveSmallIntegerField, Max)
from django.utils.encoding import python_2_unicode_compatible
from easy_thumbnails.files import get_thumbnailer
from image_cropping import ImageRatioField
from accounts.models import _get_valid_modelnames_func
from cache_tools import cached_ugettext_lazy as _
from libretto.models.common import PublishedModel


def get_default_position():
    max_pos = Diapositive.objects.aggregate(max_pos=Max('position'))['max_pos']
    if max_pos is None:
        return 0
    return max_pos + 1


@python_2_unicode_compatible
class Diapositive(PublishedModel):
    # TODO: Pouvoir paramétrer :
    #       couleur de fond, placement vertical, largeur du texte.
    # TODO: Ajuster automatiquement h1, h2, h3, ou h4 en fonction
    #       du nombre de caractères du titre court.

    # Objet lié
    content_type = ForeignKey(
        ContentType, limit_choices_to={
            'model__in': _get_valid_modelnames_func(autorites_only=False)},
        verbose_name=_('type d’objet lié'))
    object_id = PositiveIntegerField(_('identifiant de l’objet lié'))
    content_object = GenericForeignKey()
    content_object.short_description = _('objet lié')
    # Contenu
    title = CharField(_('titre'), max_length=70)
    subtitle = CharField(_('sous-titre'), max_length=100)
    ALIGNEMENT_CHOICES = (
        ('text-left', _('Gauche')),
        ('text-center', _('Centre')),
        ('text-right', _('Droite')),
    )
    text_align = CharField(_('alignement du texte'), max_length=11,
                           choices=ALIGNEMENT_CHOICES, default='text-left')
    text_background = BooleanField(
        _('cadre derrière le texte'),
        help_text=_('Ajoute un cadre semi-transparent derrière le texte '
                    'pour faciliter la lecture.'))
    image = ImageField(_('image'), upload_to='accueil')
    cropping = ImageRatioField(
        'image', '450x450', free_crop=True, size_warning=True,
        verbose_name=_('découpage de l’image'))
    image_align = CharField(_('alignement de l’image'), max_length=11,
                            choices=ALIGNEMENT_CHOICES, default='text-right')
    OPACITIES = [(Decimal(str(k)), v) for k, v in (
        (1.0, _('Opaque')),
        (0.9, _('90 %')),
        (0.8, _('80 %')),
        (0.7, _('70 %')),
        (0.6, _('60 %')),
        (0.5, _('50 %')),
        (0.4, _('40 %')),
        (0.3, _('30 %')),
        (0.2, _('20 %')),
        (0.1, _('10 %')),
    )]
    opacity = DecimalField(_('opacité'), max_digits=2, decimal_places=1,
                           default=0.6, choices=OPACITIES)
    position = PositiveSmallIntegerField(
        _('position'), default=get_default_position, unique=True)

    SLIDER_LG_WIDTH = 1140
    SLIDER_MD_WIDTH = 940
    SLIDER_SM_WIDTH = 720
    SLIDER_HEIGHT = 450
    SLIDER_LG_RATIO = SLIDER_LG_WIDTH / SLIDER_HEIGHT
    SLIDER_MD_RATIO = SLIDER_MD_WIDTH / SLIDER_HEIGHT
    SLIDER_SM_RATIO = SLIDER_SM_WIDTH / SLIDER_HEIGHT

    class Meta(object):
        verbose_name = _('diapositive')
        verbose_name_plural = _('diapositives')
        ordering = ('position',)

    def __str__(self):
        return self.title

    def box(self, slider_ratio):
        x1, y1, x2, y2 = [int(n) for n in self.cropping.split(',')]
        w, h = self.size(slider_ratio)
        x1 += ((x2 - x1) - w) // 2
        return ','.join([str(n) for n in (x1, y1, x1 + w, y1 + h)])

    def size(self, slider_ratio):
        x1, y1, x2, y2 = [int(n) for n in self.cropping.split(',')]
        w = x2 - x1
        h = y2 - y1
        if w / h > slider_ratio:
            w = int(h * slider_ratio)
        return w, h

    def box_lg(self):
        return self.box(self.SLIDER_LG_RATIO)

    def box_md(self):
        return self.box(self.SLIDER_MD_RATIO)

    def box_sm(self):
        return self.box(self.SLIDER_SM_RATIO)

    def size_lg(self):
        return self.size(self.SLIDER_LG_RATIO)

    def size_md(self):
        return self.size(self.SLIDER_MD_RATIO)

    def size_sm(self):
        return self.size(self.SLIDER_SM_RATIO)

    def thumbnail(self):
        cropping_field = self._meta.get_field('cropping')
        width = cropping_field.width
        height = cropping_field.height
        thumbnail_url = get_thumbnailer(self.image).get_thumbnail({
            'size': (150, 150),
            'box': self.cropping,
        }).url
        return '<img src="%s" style="width: %s; height: %s;" />' \
               % (thumbnail_url, width, height)
    thumbnail.short_description = _('miniature')
    thumbnail.allow_tags = True
