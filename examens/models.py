from django.apps import apps
from django.conf import settings

from django.core.validators import MinValueValidator
from django.db.models import (
    Model, PositiveSmallIntegerField, TextField, FloatField, ForeignKey,
    OneToOneField, ManyToManyField, BooleanField, DateTimeField, QuerySet,
    Max, Sum, F, SET_NULL, CASCADE)
from django.utils.encoding import force_text
from django.utils.formats import date_format
from django.utils.translation import ugettext_lazy as _

from common.utils.file import FileAnalyzer
from examens.utils import AnnotatedDiff


class Level(Model):
    number = PositiveSmallIntegerField(
        _('numéro'), unique=True, default=1,
        validators=[MinValueValidator(1)])
    help_message = TextField(_('message d’aide'))
    sources = ManyToManyField(
        'libretto.Source', through='LevelSource', related_name='+',
        verbose_name=_('sources'))

    class Meta:
        verbose_name = _('niveau')
        verbose_name_plural = _('niveaux')
        ordering = ('number',)

    def __str__(self):
        return force_text(self.number)


def limit_choices_to_possible_sources():
    return {'pk__in': (
        apps.get_model('libretto.Source').objects.exclude(transcription='')
        .filter(type_fichier=FileAnalyzer.IMAGE)
    )}


class LevelSource(Model):
    level = ForeignKey(Level, related_name='level_sources', on_delete=CASCADE,
                       verbose_name=_('niveau'))
    source = OneToOneField(
        'libretto.source', limit_choices_to=limit_choices_to_possible_sources,
        related_name='+', verbose_name=_('source'), on_delete=CASCADE)

    class Meta:
        verbose_name = _('source de niveau')
        verbose_name_plural = _('sources de niveau')


class TakenExamQuerySet(QuerySet):
    def get_for_request(self, request):
        if request.user.is_authenticated:
            return self.get_or_create(user=request.user)[0]
        if not request.session.modified:
            request.session.save()
        session = apps.get_model('sessions.Session').objects.get(
            pk=request.session.session_key)
        return self.get_or_create(session=session)[0]

    def annotate_time_spent(self):
        return self.annotate(_time_spent=Sum(F('taken_levels__end')
                                             - F('taken_levels__start')))


class TakenExam(Model):
    user = OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=CASCADE,
        related_name='+', verbose_name=_('utilisateur'))
    session = OneToOneField(
        'sessions.Session', null=True, blank=True, verbose_name=_('session'),
        on_delete=SET_NULL, editable=False, related_name='+')

    objects = TakenExamQuerySet.as_manager()
    objects.use_for_related_fields = True

    class Meta:
        verbose_name = _('examen passé')
        verbose_name_plural = _('examens passés')
        ordering = ('user', 'session')

    def __str__(self):
        return force_text(self.session if self.user is None else self.user)

    @property
    def last_passed_level_number(self):
        last_passed_level_number = self.taken_levels.filter(
            passed=True).aggregate(n=Max('level__number'))['n']
        if last_passed_level_number is None:
            return 0
        return last_passed_level_number

    # TODO: Probably move this method somewhere else.
    @property
    def max_level_number(self):
        return Level.objects.aggregate(n=Max('number'))['n']

    def is_complete(self):
        return self.last_passed_level_number == self.max_level_number
    is_complete.short_description = _('est fini')
    is_complete.boolean = True

    @property
    def current_level(self):
        if not hasattr(self, '_current_level'):
            self._current_level = Level.objects.get(
                number=self.last_passed_level_number + 1)
        return self._current_level

    def get_time_spent(self):
        if not hasattr(self, '_time_spent'):
            self._time_spent = self._meta.model.objects.filter(
                pk=self.pk).annotate_time_spent()[0]._time_spent
        return self._time_spent
    get_time_spent.short_description = _('temps passé')
    get_time_spent.admin_order_field = '_time_spent'

    @property
    def last_taken_level(self):
        return self.taken_levels.was_sent().order_by('-start').first()

    def take_level(self):
        current_level = self.current_level
        taken_level = TakenLevel(taken_exam=self, level=current_level)
        taken_for_this_level = self.taken_levels.filter(
            level=self.current_level).order_by('-start')
        last_sent_level = taken_for_this_level.was_sent().first()
        already_taken_level = taken_for_this_level.first()
        if already_taken_level is None:
            taken_level.source = current_level.sources.order_by('?')[0]
        elif not already_taken_level.was_sent:
            return already_taken_level
        else:
            taken_level.source = already_taken_level.source
            if last_sent_level is not None:
                taken_level.transcription = last_sent_level.transcription
        taken_level.save()
        return taken_level


class TakenLevelQuerySet(QuerySet):
    def was_sent(self):
        return self.filter(end__isnull=False)


class TakenLevel(Model):
    taken_exam = ForeignKey(TakenExam, related_name='taken_levels',
                            verbose_name=_('examen passé'), editable=False,
                            on_delete=CASCADE)
    level = ForeignKey(
        Level, verbose_name=_('niveau'), editable=False, related_name='+',
        on_delete=CASCADE)
    source = ForeignKey(
        'libretto.Source', verbose_name=_('source'), editable=False,
        related_name='+', on_delete=CASCADE)
    transcription = TextField(verbose_name=_('transcription'))
    score = FloatField(_('note'), null=True, blank=True, editable=False)
    MAX_SCORE = 1.0
    passed = BooleanField(_('passé'), default=False)
    start = DateTimeField(_('début'), auto_now_add=True)
    end = DateTimeField(_('fin'), null=True, blank=True, editable=False)

    objects = TakenLevelQuerySet.as_manager()
    objects.use_for_related_fields = True

    class Meta:
        verbose_name = _('niveau passé')
        verbose_name_plural = _('niveaux passés')
        ordering = ('start',)

    def __str__(self):
        return '%s, %s' % (self.level,
                           date_format(self.start, 'DATETIME_FORMAT'))

    def save(self, *args, **kwargs):
        if self.was_sent:
            self.score = self.diff.get_score()
            self.passed = self.score >= self.MAX_SCORE
        super(TakenLevel, self).save(*args, **kwargs)

    @property
    def diff(self):
        if not hasattr(self, '_diff'):
            self._diff = AnnotatedDiff(self.transcription,
                                       self.source.transcription)
        return self._diff

    @property
    def diff_html(self):
        return self.diff.get_html()

    @property
    def errors(self):
        return self.diff.errors

    @property
    def was_sent(self):
        return self.end is not None
