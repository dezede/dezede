# coding: utf-8

from .functions import ex, str_list, cite, no, date_html, href
from django.db.models import CharField, DateField, ForeignKey, \
                             ManyToManyField, permalink, get_model
from tinymce.models import HTMLField
from django.utils.html import strip_tags
from django.utils.translation import ungettext_lazy, ugettext, \
                                     ugettext_lazy as _
from .common import CustomModel, AutoriteModel, LOWER_MSG, PLURAL_MSG, \
                    DATE_MSG, calc_pluriel, SlugModel
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.generic import GenericRelation


class TypeDeSource(CustomModel, SlugModel):
    nom = CharField(max_length=200, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=230, blank=True,
        verbose_name=_('nom (au pluriel)'),
        help_text=PLURAL_MSG)

    class Meta:
        verbose_name = ungettext_lazy('type de source', 'types de source', 1)
        verbose_name_plural = ungettext_lazy('type de source',
                                             'types de source', 2)
        ordering = ['slug']
        app_label = 'catalogue'

    def pluriel(self):
        return calc_pluriel(self)

    def __unicode__(self):
        return self.nom


class Source(AutoriteModel):
    nom = CharField(_('nom'), max_length=200,
                    help_text=ex(_('Journal de Rouen')))
    numero = CharField(_(u'numéro'), max_length=50, blank=True,
                       help_text=_(u'Sans « № »') + '. ' + ex('52'))
    date = DateField(_('date'), help_text=DATE_MSG)
    page = CharField(_('page'), max_length=50, blank=True,
                     help_text=_(u'Sans « p. »') + '. ' + ex('3'))
    type = ForeignKey('TypeDeSource', related_name='sources',
        help_text=ex(_('compte rendu')), verbose_name=_('type'))
    contenu = HTMLField(_('contenu'), blank=True,
        help_text=_(u'Recopié tel quel, avec les fautes d’orthographe suivies '
                    u'de « [<em>sic</em>] » le cas échéant.'))
    auteurs = GenericRelation('Auteur')
    evenements = ManyToManyField('Evenement', related_name='sources',
        blank=True, null=True, verbose_name=_(u'événements'))

    @permalink
    def get_absolute_url(self):
        return 'source_pk', [self.pk]

    def permalien(self):
        return self.get_absolute_url()

    def link(self):
        return self.html()
    link.short_description = _('Lien')
    link.allow_tags = True

    def individus_auteurs(self):
        return self.auteurs.individus()

    def auteurs_html(self, tags=True):
        return self.auteurs.html(tags)

    def date_html(self, tags=True):
        return date_html(self.date, tags)

    def no(self):
        return no(self.numero)

    def p(self):
        return ugettext('p. %s') % self.page

    def html(self, tags=True):
        url = None if not tags else self.get_absolute_url()
        l = [cite(self.nom, tags)]
        if self.numero:
            l.append(self.no())
        l.append(self.date_html(tags))
        if self.page:
            l.append(self.p())
        out = ', '.join(l)
        return mark_safe(href(url, out, tags))
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def has_events(self):
        return self.evenements.exists()
    has_events.short_description = _(u'Événements')
    has_events.boolean = True
    has_events.admin_order_field = 'evenements'

    def has_program(self):
        if not self.has_events():
            return False
        for e in self.evenements.all():
            if not e.has_program():
                return False
        return True
    has_program.short_description = _('Programme')
    has_program.boolean = True

    class Meta:
        verbose_name = ungettext_lazy('source', 'sources', 1)
        verbose_name_plural = ungettext_lazy('source', 'sources', 2)
        ordering = ['date', 'nom', 'numero', 'page', 'type']
        app_label = 'catalogue'

    def __unicode__(self):
        return strip_tags(self.html(False))
