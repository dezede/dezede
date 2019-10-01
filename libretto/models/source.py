import json
from pathlib import Path

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db.models import (
    CharField, ForeignKey, ManyToManyField, permalink, PROTECT, URLField,
    CASCADE, PositiveSmallIntegerField, FileField, BooleanField, Prefetch)
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _
from easy_thumbnails.alias import aliases
from easy_thumbnails.files import get_thumbnailer
from tinymce.models import HTMLField
from .base import (
    CommonModel, AutoriteModel, LOWER_MSG, PLURAL_MSG, calc_pluriel,
    SlugModel, PublishedManager, PublishedQuerySet, AncrageSpatioTemporel,
)

from common.utils.base import OrderedDefaultDict
from common.utils.file import FileAnalyzer
from common.utils.html import cite, href, small, hlp
from common.utils.text import ex, str_list
from typography.models import TypographicModel


__all__ = (
    'TypeDeSource', 'Source', 'Audio', 'Video',
    'SourceEvenement', 'SourceOeuvre', 'SourceIndividu', 'SourceEnsemble',
    'SourceLieu', 'SourcePartie'
)


class TypeDeSource(CommonModel, SlugModel):
    nom = CharField(_('nom'), max_length=200, help_text=LOWER_MSG, unique=True,
                    db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
                            db_index=True, help_text=PLURAL_MSG)
    # TODO: Ajouter un classement et changer ordering en conséquence.

    class Meta(object):
        verbose_name = _('type de source')
        verbose_name_plural = _('types de source')
        ordering = ('slug',)

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        if all_relations:
            return ('sources',)
        return ()

    def pluriel(self):
        return calc_pluriel(self)

    def __str__(self):
        return self.nom


class SourceQuerySet(PublishedQuerySet):
    def group_by_type(self):
        sources = OrderedDefaultDict()
        for source in self:
            sources[source.type].append(source)
        return sources.items()

    def prefetch(self):
        return self.select_related('type').only(
            'titre', 'numero', 'folio', 'page', 'lieu_conservation',
            'cote', 'url', 'transcription', 'date', 'date_approx',
            'type__nom', 'type__nom_pluriel', 'fichier', 'type_fichier',
        )

    def with_video(self):
        return self.filter(type_fichier=FileAnalyzer.VIDEO)

    def with_audio(self):
        return self.filter(type_fichier=FileAnalyzer.AUDIO)

    def with_image(self):
        return self.filter(type_fichier=FileAnalyzer.IMAGE)

    def with_other(self):
        return self.filter(type_fichier=FileAnalyzer.OTHER)

    def with_text(self):
        return self.exclude(transcription='')

    def with_link(self):
        return self.exclude(url='')

    def with_data_type(self, data_type):
        if data_type == Source.VIDEO:
            return self.with_video()
        if data_type == Source.AUDIO:
            return self.with_audio()
        if data_type == Source.IMAGE:
            return self.with_image()
        if data_type == Source.OTHER:
            return self.with_other()
        if data_type == Source.TEXT:
            return self.with_text()
        if data_type == Source.LINK:
            return self.with_link()
        raise ValueError('Unknown data type.')


class SourceManager(PublishedManager):
    queryset_class = SourceQuerySet

    def group_by_type(self):
        return self.get_queryset().group_by_type()

    def prefetch(self):
        return self.get_queryset().prefetch()

    def with_video(self):
        return self.get_queryset().with_video()

    def with_audio(self):
        return self.get_queryset().with_audio()

    def with_image(self):
        return self.get_queryset().with_image()

    def with_other(self):
        return self.get_queryset().with_other()

    def with_text(self):
        return self.get_queryset().with_text()

    def with_link(self):
        return self.get_queryset().with_link()

    def with_data_type(self, data_type):
        return self.get_queryset().with_data_type(data_type)


class Source(AutoriteModel):
    parent = ForeignKey(
        'self', related_name='children', verbose_name=_('parent'),
        null=True, blank=True, on_delete=CASCADE,
        help_text=_(
            'À remplir par exemple si la source est une page d’un recueil '
            'déjà existant ou un tome d’une série.'
        ),
    )
    position = PositiveSmallIntegerField(
        _('position'), null=True, blank=True,
        help_text=_('Position au sein de son parent.')
    )
    est_promu = BooleanField(_('est dans la bibliothèque'), default=False)

    type = ForeignKey('TypeDeSource', related_name='sources',
                      help_text=ex(_('compte rendu')), verbose_name=_('type'),
                      on_delete=PROTECT)
    titre = CharField(_('titre'), max_length=200, blank=True, db_index=True,
                      help_text=ex(_('Journal de Rouen')))
    legende = CharField(_('légende'), max_length=600, blank=True,
                        help_text=_('Recommandée pour les images.'))

    ancrage = AncrageSpatioTemporel(has_heure=False, has_lieu=False)
    numero = CharField(_('numéro'), max_length=50, blank=True, db_index=True,
                       help_text=_('Sans « № ». Exemple : « 52 »'))
    folio = CharField(_('folio'), max_length=10, blank=True,
                      help_text=_('Sans « f. ». Exemple : « 3 ».'))
    page = CharField(_('page'), max_length=10, blank=True, db_index=True,
                     help_text=_('Sans « p. ». Exemple : « 3 »'))
    lieu_conservation = CharField(_('lieu de conservation'), max_length=50,
                                  blank=True, db_index=True)
    cote = CharField(_('cote'), max_length=60, blank=True, db_index=True)
    url = URLField(_('URL'), blank=True,
                   help_text=_('Uniquement un permalien extérieur à Dezède.'))

    transcription = HTMLField(
        _('transcription'), blank=True,
        help_text=_('Recopier la source ou un extrait en suivant les règles '
                    'définies dans '  # FIXME: Don’t hardcode the URL.
                    '<a href="/examens/source">le didacticiel.</a>'),
    )

    fichier = FileField(_('fichier'), upload_to='files/', blank=True)
    TYPES = (
        (FileAnalyzer.OTHER, _('autre')),
        (FileAnalyzer.IMAGE, _('image')),
        (FileAnalyzer.AUDIO, _('audio')),
        (FileAnalyzer.VIDEO, _('vidéo')),
    )
    type_fichier = PositiveSmallIntegerField(
        choices=TYPES, null=True, blank=True, editable=False, db_index=True,
    )

    evenements = ManyToManyField(
        'Evenement', through='SourceEvenement', related_name='sources',
        verbose_name=_('événements'))
    oeuvres = ManyToManyField('Oeuvre', through='SourceOeuvre',
                              related_name='sources', verbose_name=_('œuvres'))
    individus = ManyToManyField(
        'Individu', through='SourceIndividu', related_name='sources',
        verbose_name=_('individus'))
    ensembles = ManyToManyField(
        'Ensemble', through='SourceEnsemble', related_name='sources',
        verbose_name=_('ensembles'))
    lieux = ManyToManyField('Lieu', through='SourceLieu',
                            related_name='sources', verbose_name=_('lieux'))
    parties = ManyToManyField(
        'Partie', through='SourcePartie', related_name='sources',
        verbose_name=_('sources'))

    objects = SourceManager()

    class Meta:
        verbose_name = _('source')
        verbose_name_plural = _('sources')
        ordering = (
            'date', 'titre', 'numero',
            'parent__date', 'parent__titre', 'parent__numero',
            'position', 'page',
            'lieu_conservation', 'cote',
        )
        permissions = (('can_change_status', _('Peut changer l’état')),)

    def __str__(self):
        return strip_tags(self.html(False))

    @cached_property
    def specific(self):
        if self.type_fichier == FileAnalyzer.AUDIO:
            return Audio.objects.get(pk=self.pk)
        if self.type_fichier == FileAnalyzer.VIDEO:
            return Video.objects.get(pk=self.pk)
        return self

    @permalink
    def get_absolute_url(self):
        return 'source_permanent_detail', (self.pk,)

    @permalink
    def get_change_url(self):
        meta = self.specific._meta
        return f'admin:{meta.app_label}_{meta.model_name}_change', (self.pk,)

    def permalien(self):
        return self.get_absolute_url()

    def link(self):
        return self.html()
    link.short_description = _('Lien')
    link.allow_tags = True

    def auteurs_html(self, tags=True):
        return self.auteurs.html(tags)

    def no(self):
        return ugettext('n° %s') % self.numero

    def f(self):
        return ugettext('f. %s') % self.folio

    def p(self):
        return ugettext('p. %s') % self.page

    def html(self, tags=True, pretty_title=False, link=True):
        url = None if not tags else self.get_absolute_url()
        conservation = hlp(self.lieu_conservation,
                           ugettext('Lieu de conservation'), tags)
        if self.ancrage.date or self.ancrage.date_approx:
            ancrage = hlp(self.ancrage.html(tags, caps=False), ugettext('date'))
        else:
            ancrage = None
        if self.cote:
            conservation += f", {hlp(self.cote, 'cote', tags)}"
        if self.titre:
            l = [cite(self.titre, tags)]
            if self.numero:
                l.append(self.no())
            if ancrage is not None:
                l.append(ancrage)
            if self.lieu_conservation:
                l[-1] += f' ({conservation})'
        else:
            l = [conservation]
            if ancrage is not None:
                l.append(ancrage)
        if self.folio:
            l.append(hlp(self.f(), ugettext('folio'), tags))
        if self.page:
            l.append(hlp(self.p(), ugettext('page'), tags))
        if self.parent is not None:
            l.insert(
                0, self.parent.html(tags=tags, pretty_title=pretty_title,
                                    link=pretty_title)
            )
        l = (l[0], small(str_list(l[1:]), tags=tags)) if pretty_title else l
        out = str_list(l)
        if link:
            return mark_safe(href(url, out, tags))
        return out
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def pretty_title(self):
        return self.html(pretty_title=True, link=False)

    def has_events(self):
        if hasattr(self, '_has_events'):
            return self._has_events
        return self.evenements.exists()
    has_events.short_description = _('événements')
    has_events.boolean = True
    has_events.admin_order_field = 'evenements'

    def has_program(self):
        if hasattr(self, '_has_program'):
            return self._has_program
        return self.evenements.with_program().exists()
    has_program.short_description = _('programme')
    has_program.boolean = True

    def is_other(self):
        return self.type_fichier == FileAnalyzer.OTHER

    def is_pdf(self):
        return self.is_other() and self.fichier.name.endswith('.pdf')

    def is_image(self):
        return self.type_fichier == FileAnalyzer.IMAGE

    def is_audio(self):
        return self.type_fichier == FileAnalyzer.AUDIO

    def is_video(self):
        return self.type_fichier == FileAnalyzer.VIDEO

    def has_children_images(self):
        return self.children.filter(type_fichier=FileAnalyzer.IMAGE).exists()

    def has_images(self):
        return (
            self.type_fichier == FileAnalyzer.IMAGE
            or self.has_children_images()
        )

    def has_fichiers(self):
        return (
            self.is_other() or self.is_audio() or self.is_video()
            or self.has_images()
        )

    @cached_property
    def images(self):
        images = []
        if self.is_image():
            images.append(self)

        images.extend(
            self.children.filter(
                type_fichier=FileAnalyzer.IMAGE
            ).order_by('position', 'page'))
        return images

    def is_empty(self):
        return not (self.transcription or self.url or self.has_fichiers())

    DATA_TYPES = ('video', 'audio', 'image', 'other', 'text', 'link')
    VIDEO, AUDIO, IMAGE, OTHER, TEXT, LINK = DATA_TYPES

    @property
    def data_types(self):
        data_types = []
        if self.is_video():
            data_types.append(self.VIDEO)
        if self.is_audio():
            data_types.append(self.AUDIO)
        if self.has_images():
            data_types.append(self.IMAGE)
        if self.is_other():
            data_types.append(self.OTHER)
        if self.transcription:
            data_types.append(self.TEXT)
        if self.url:
            data_types.append(self.LINK)
        return data_types

    ICONS = {
        VIDEO: '<i class="fa fa-fw fa-video-camera"></i>',
        AUDIO: '<i class="fa fa-fw fa-volume-up"></i>',
        IMAGE: '<i class="fa fa-fw fa-photo"></i>',
        OTHER: '<i class="fa fa-fw fa-paperclip"></i>',
        TEXT: '<i class="fa fa-fw fa-file-text-o"></i>',
        LINK: '<i class="fa fa-fw fa-external-link"></i>',
    }

    DATA_TYPES_WITH_ICONS = (
        (VIDEO, _(f'{ICONS[VIDEO]} Vidéo')),
        (AUDIO, _(f'{ICONS[AUDIO]} Audio')),
        (IMAGE, _(f'{ICONS[IMAGE]} Image')),
        (OTHER, _(f'{ICONS[OTHER]} Autre')),
        (TEXT, _(f'{ICONS[TEXT]} Texte')),
        (LINK, _(f'{ICONS[LINK]} Lien')),
    )

    @property
    def icons(self):
        return ''.join([self.ICONS[data_type]
                        for data_type in self.data_types])

    def update_media_info(self):
        if self.fichier:
            file_analyzer = FileAnalyzer(self, 'fichier')
            self.type_fichier = file_analyzer.type
        else:
            self.type_fichier = None

    def clean(self):
        super().clean()
        if not getattr(self, 'updated_media_info', False):
            self.update_media_info()
            self.updated_media_info = True

    @cached_property
    def first_page(self):
        return self.children.order_by('position').first()

    @cached_property
    def prev_page(self):
        if self.parent is not None:
            return self.parent.children.exclude(pk=self.pk).filter(
                position__lte=self.position,
            ).order_by('-position').first()

    @cached_property
    def next_page(self):
        if self.parent is not None:
            return self.parent.children.exclude(pk=self.pk).filter(
                position__gte=self.position,
            ).order_by('position').first()

    @property
    def filename(self):
        return Path(self.fichier.path).name

    @cached_property
    def linked_individus(self):
        return self.individus.distinct()

    @cached_property
    def linked_evenements(self):
        return self.evenements.distinct()

    @cached_property
    def linked_oeuvres(self):
        return self.oeuvres.distinct()

    @cached_property
    def linked_ensembles(self):
        return self.ensembles.distinct()

    @cached_property
    def linked_lieux(self):
        return self.lieux.distinct()

    @cached_property
    def linked_parties(self):
        return self.parties.distinct()

    def get_linked_objects(self):
        return [
            *self.auteurs.all(),
            *self.linked_individus,
            *self.linked_evenements,
            *self.linked_oeuvres,
            *self.linked_ensembles,
            *self.linked_lieux,
            *self.linked_parties,
        ]

    def get_linked_objects_json(self):
        return json.dumps([
            {
                'url': obj.get_absolute_url(), 'label': str(obj),
                'model': obj.class_name().lower(),
            }
            for obj in self.get_linked_objects()
        ])

    def nested_evenements(self):
        return apps.get_model('libretto.Evenement').objects.filter(
            sources__in=self.children.all() | Source.objects.filter(pk=self.pk)
        ).distinct()

    def nested_oeuvres(self):
        return apps.get_model('libretto.Oeuvre').objects.filter(
            sources__in=self.children.all() | Source.objects.filter(pk=self.pk)
        ).distinct()

    def nested_individus(self):
        return apps.get_model('libretto.Individu').objects.filter(
            sources__in=self.children.all() | Source.objects.filter(pk=self.pk)
        ).distinct()

    def nested_ensembles(self):
        return apps.get_model('libretto.Ensemble').objects.filter(
            sources__in=self.children.all() | Source.objects.filter(pk=self.pk)
        ).distinct()

    def nested_lieux(self):
        return apps.get_model('libretto.Lieu').objects.filter(
            sources__in=self.children.all() | Source.objects.filter(pk=self.pk)
        ).distinct()

    def nested_parties(self):
        return apps.get_model('libretto.Partie').objects.filter(
            sources__in=self.children.all() | Source.objects.filter(pk=self.pk)
        ).distinct()

    @property
    def small_thumbnail(self):
        if self.is_image():
            thumbnailer = get_thumbnailer(self.fichier)
            return thumbnailer.get_thumbnail(aliases.get('small')).url

    @property
    def medium_thumbnail(self):
        if self.is_image():
            thumbnailer = get_thumbnailer(self.fichier)
            return thumbnailer.get_thumbnail(aliases.get('medium')).url


class AudioVideoAbstract(Source):
    fichier_ogg = FileField(
        _('fichier (OGG)'), upload_to='files/ogg/', blank=True, editable=False,
    )
    fichier_mpeg = FileField(
        _('fichier (MPEG)'), upload_to='files/mpeg/', blank=True,
        editable=False,
    )
    extrait = FileField(_('extrait'), upload_to='files/extraits/', blank=True)
    extrait_ogg = FileField(
        _('extrait (OGG)'), upload_to='files/extraits/ogg/', blank=True,
        editable=False,
    )
    extrait_mpeg = FileField(
        _('extrait (MPEG)'), upload_to='files/extraits/mpeg/', blank=True,
        editable=False,
    )
    format = CharField(_('format'), max_length=10, blank=True, editable=False)
    format_extrait = CharField(
        _('format de l’extrait'), max_length=10, blank=True, editable=False,
    )
    duree = PositiveSmallIntegerField(
        _('durée (en secondes)'), null=True, blank=True,
        editable=False,
    )
    duree_extrait = PositiveSmallIntegerField(
        _('durée de l’extrait (en secondes)'), null=True, blank=True,
        editable=False,
    )

    type_fichier_attendu = None
    format_ogg_attendu = 'ogg'
    format_mpeg_attendu = 'mpeg'

    class Meta:
        abstract = True

    def update_media_info(self):
        if not self.fichier and not self.extrait:
            raise ValidationError(
                _('Vous devez remplir au moins « fichier » ou « extrait ».')
            )

        if self.fichier:
            file_analyzer = FileAnalyzer(self, 'fichier')
            file_analyzer.validate(expected_type=self.type_fichier_attendu)

            self.format = file_analyzer.format_name
            self.duree = file_analyzer.avprobe_info.duration
            if isinstance(self, Video):
                self.largeur = file_analyzer.avprobe_info.width
                self.hauteur = file_analyzer.avprobe_info.height

            if self.fichier_ogg:
                file_analyzer = FileAnalyzer(self, 'fichier_ogg')
                file_analyzer.validate(
                    expected_type=self.type_fichier_attendu,
                    expected_format=self.format_ogg_attendu,
                )
            if self.fichier_mpeg:
                file_analyzer = FileAnalyzer(self, 'fichier_mpeg')
                file_analyzer.validate(
                    expected_type=self.type_fichier_attendu,
                    expected_format=self.format_mpeg_attendu,
                )

        if self.extrait:
            file_analyzer = FileAnalyzer(self, 'extrait')
            file_analyzer.validate(expected_type=self.type_fichier_attendu)

            self.format_extrait = file_analyzer.format_name
            self.duree_extrait = file_analyzer.avprobe_info.duration
            if isinstance(self, Video):
                self.largeur_extrait = file_analyzer.avprobe_info.width
                self.hauteur_extrait = file_analyzer.avprobe_info.height

            if self.extrait_ogg:
                file_analyzer = FileAnalyzer(self, 'extrait_ogg')
                file_analyzer.validate(
                    expected_type=self.type_fichier_attendu,
                    expected_format=self.format_ogg_attendu,
                )
            if self.extrait_mpeg:
                file_analyzer = FileAnalyzer(self, 'extrait_mpeg')
                file_analyzer.validate(
                    expected_type=self.type_fichier_attendu,
                    expected_format=self.format_mpeg_attendu,
                )

        self.type_fichier = self.type_fichier_attendu


class Audio(AudioVideoAbstract):
    type_fichier_attendu = FileAnalyzer.AUDIO
    format_mpeg_attendu = 'mp3'

    class Meta:
        verbose_name = _('audio')
        verbose_name_plural = _('audios')


class Video(AudioVideoAbstract):
    largeur = PositiveSmallIntegerField(_('largeur'), null=True, blank=True,
                                        editable=False)
    hauteur = PositiveSmallIntegerField(_('hauteur'), null=True, blank=True,
                                        editable=False)
    largeur_extrait = PositiveSmallIntegerField(
        _('largeur de l’extrait'), null=True, blank=True, editable=False,
    )
    hauteur_extrait = PositiveSmallIntegerField(
        _('hauteur de l’extrait'), null=True, blank=True, editable=False,
    )

    type_fichier_attendu = FileAnalyzer.VIDEO
    format_mpeg_attendu = 'mp4'

    class Meta:
        verbose_name = _('vidéo')
        verbose_name_plural = _('vidéos')


class SourceEvenement(TypographicModel):
    source = ForeignKey(Source, related_name='sourceevenement_set',
                        on_delete=CASCADE)
    evenement = ForeignKey('Evenement', verbose_name=_('événement'),
                           related_name='sourceevenement_set',
                           on_delete=CASCADE)

    class Meta(object):
        db_table = 'libretto_source_evenements'
        unique_together = ('source', 'evenement')


class SourceOeuvre(TypographicModel):
    source = ForeignKey(Source, related_name='sourceoeuvre_set',
                        on_delete=CASCADE)
    oeuvre = ForeignKey('Oeuvre', verbose_name=_('œuvre'),
                        related_name='sourceoeuvre_set',
                        on_delete=CASCADE)

    class Meta(object):
        db_table = 'libretto_source_oeuvres'
        unique_together = ('source', 'oeuvre')


class SourceIndividu(TypographicModel):
    source = ForeignKey(Source, related_name='sourceindividu_set',
                        on_delete=CASCADE)
    individu = ForeignKey('Individu', verbose_name=_('individu'),
                          related_name='sourceindividu_set',
                          on_delete=CASCADE)

    class Meta(object):
        db_table = 'libretto_source_individus'
        unique_together = ('source', 'individu')


class SourceEnsemble(TypographicModel):
    source = ForeignKey(Source, related_name='sourceensemble_set',
                        on_delete=CASCADE)
    ensemble = ForeignKey('Ensemble', verbose_name=_('ensemble'),
                          related_name='sourceensemble_set',
                          on_delete=CASCADE)

    class Meta(object):
        db_table = 'libretto_source_ensembles'
        unique_together = ('source', 'ensemble')


class SourceLieu(TypographicModel):
    source = ForeignKey(Source, related_name='sourcelieu_set',
                        on_delete=CASCADE)
    lieu = ForeignKey('Lieu', verbose_name=_('lieu'),
                      related_name='sourcelieu_set',
                      on_delete=CASCADE)

    class Meta(object):
        db_table = 'libretto_source_lieux'
        unique_together = ('source', 'lieu')


class SourcePartie(TypographicModel):
    source = ForeignKey(Source, related_name='sourcepartie_set',
                        on_delete=CASCADE)
    partie = ForeignKey('Partie', verbose_name=_('rôle ou instrument'),
                        related_name='sourcepartie_set', on_delete=CASCADE)

    class Meta(object):
        db_table = 'libretto_source_parties'
        unique_together = ('source', 'partie')
