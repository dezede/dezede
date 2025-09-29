from django.db.models import (
    OneToOneField, CharField, PositiveIntegerField, TextField, CASCADE,
)
from django.utils.translation import gettext_lazy as _
from libretto.models import Evenement, Lieu
from libretto.models.base import CommonModel

__all__ = ('EvenementAFO', 'LieuAFO')


class EvenementAFO(CommonModel):
    evenement = OneToOneField(Evenement, related_name='afo',
                              verbose_name=_('événement'), on_delete=CASCADE)
    nom_festival = CharField(_('nom du festival'), max_length=80, blank=True)
    tournee = CharField(_('code ou titre de la tournée'), max_length=60,
                        blank=True)
    cycle = CharField(_('cycle'), max_length=40, blank=True)
    code_programme = CharField(_('code du programme'), max_length=60,
                               blank=True)
    titre_programme = CharField(_('titre du programme'), max_length=200,
                                blank=True)
    TYPES_DE_PROGRAMMES = (
        ('LS', _('lyrique version scénique')),
        ('MC', _('musique de chambre')),
        ('LC', _('lyrique version concert')),
        ('S', _('symphonique (dont chœur/récital)')),
        ('C', _('chorégraphique')),
        ('A', _('autre')),
    )
    type_de_programme = CharField(_('typologie artistique du programme'),
                                  max_length=2, blank=True,
                                  choices=TYPES_DE_PROGRAMMES)
    PRESENTATIONS_SPECIFIQUES = (
        ('C', _('concert commenté/présenté')),
        ('P', _('concert participatif')),
        ('A', _('autre')),
    )
    presentation_specifique = CharField(_('présentation spécifique'),
                                        max_length=1, blank=True,
                                        choices=PRESENTATIONS_SPECIFIQUES)
    PUBLICS_SPECIFIQUES = (
        ('P', _('public de proximité')),
        ('E', _('public empêché (santé, handicap, justice)')),
        ('S', _('seniors')),
        ('J', _('jeunes')),
        ('JS', _('jeunes en temps scolaire')),
        ('JV', _('jeunes hors temps scolaire')),
    )
    public_specifique = CharField(_('public spécifique'), max_length=2,
                                  blank=True, choices=PUBLICS_SPECIFIQUES)
    MODALITES_DE_PRODUCTION = (
        ('P', _('participation aux frais')),
        ('A', _('autoproduction')),
        ('Ce', _('contrat de cession')),
        ('Cp', _('contrat de coproduction')),
        ('Cr', _('contrat de coréalisation')),
        ('L', _('location')),  # TODO: Pas sûr que ce soit une bonne valeur.
    )
    modalite_de_production = CharField(_('modalité de production'),
                                       max_length=2, blank=True,
                                       choices=MODALITES_DE_PRODUCTION)
    permanents = PositiveIntegerField(
        _('nombre de musiciens permanents convoqués (dont remplaçants)'),
        null=True, blank=True)
    remplacants = PositiveIntegerField(
        _('nombre de musiciens remplaçants'), null=True, blank=True)
    supplementaires = PositiveIntegerField(
        _('nombre de musiciens supplémentaires convoqués'),
        null=True, blank=True)
    nomenclature = TextField(_('nomenclature'), blank=True)
    exonerees = PositiveIntegerField(_('entrées exonérées'), null=True,
                                     blank=True)
    payantes = PositiveIntegerField(_('entrées payantes'), null=True,
                                    blank=True)
    scolaires = PositiveIntegerField(_('entrées scolaires'), null=True,
                                     blank=True)
    frequentation = PositiveIntegerField(_('fréquentation totale'), null=True,
                                         blank=True)
    jauge = PositiveIntegerField(_('jauge'), null=True, blank=True)

    class Meta(object):
        verbose_name = _('événement AFO')
        verbose_name_plural = _('événements AFO')

    def __str__(self):
        return str(self.evenement)


class LieuAFO(CommonModel):
    lieu = OneToOneField(Lieu, related_name='afo', on_delete=CASCADE,
                         verbose_name=_('lieu ou institution'))
    code_postal = CharField(_('code postal'), max_length=10, blank=True)
    TYPES_DE_SCENES = (
        ('N', _('nationale')),
        ('C', _('conventionnée')),
    )
    type_de_scene = CharField(_('type de scène'), max_length=1, blank=True,
                              choices=TYPES_DE_SCENES)
    TYPES_DE_SALLES = (
        ('M', _('dédiée à la musique')),
        ('P', _('pluridisciplinaire')),
        ('A', _('autre')),
    )
    type_de_salle = CharField(_('type de salle'), max_length=1, blank=True,
                              choices=TYPES_DE_SALLES)

    class Meta(object):
        verbose_name = _('lieu ou institution AFO')
        verbose_name_plural = _('lieux et institutions AFO')

    def __str__(self):
        return str(self.lieu)
