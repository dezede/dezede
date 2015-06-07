# coding: utf-8

from __future__ import unicode_literals
from django.views.generic import FormView

from .forms import SourceExamenForm, LEVELS_DATA, LEVELS, LEVELS_HELPS
from libretto.models import Source
from .utils import highlight_diffs, get_diffs_per_normalizer


SOURCE_LEVEL_SESSION_KEY = 'examen_source_level'


class SourceExamen(FormView):
    form_class = SourceExamenForm
    template_name = 'examens/source.html'
    POINTS_BY_ERROR = {
        'texte': 0.5,
        'majuscule': 0.1,
        'espacement': 0.05,
        'ponctuation': 0.25,
        'accentuation': 0.25,
        'mise en forme': 0.05,
    }
    SUCCESS_SCORE = 18.0

    def get_initial(self):
        self.request.session[SOURCE_LEVEL_SESSION_KEY] = 4  # FIXME:
        if SOURCE_LEVEL_SESSION_KEY not in self.request.session:
            self.request.session[SOURCE_LEVEL_SESSION_KEY] = 1
        level = self.request.session[SOURCE_LEVEL_SESSION_KEY]
        source_qs = Source.objects.filter(pk__in=dict(LEVELS_DATA)[level])
        return {
            'level': level,
            'source': source_qs.order_by('?').first(),
        }

    def get_score(self, errors):
        score = 20.0
        for name, diffs in errors:
            score -= (sum([len(diff.diff_a + diff.diff_b) for diff in diffs])
                      * self.POINTS_BY_ERROR[name])
        return max(score, 0.0)

    def get_context_data(self, **kwargs):
        context = super(SourceExamen, self).get_context_data(**kwargs)
        form = context['form']
        if self.request.method == 'POST':
            context['source'] = form.cleaned_data['source']
        else:
            context['source'] = form.initial['source']
        if hasattr(self, 'diff'):
            context['diff'] = self.diff
        if hasattr(self, 'errors'):
            score = self.get_score(self.errors)
            success = form.is_valid and score >= self.SUCCESS_SCORE
            if success:
                self.request.session[SOURCE_LEVEL_SESSION_KEY] = int(
                    form.cleaned_data['level']) + 1
            context.update(
                errors=self.errors,
                score=score,
                success=success,
            )
        level = self.request.session[SOURCE_LEVEL_SESSION_KEY]
        context.update(
            level=level,
            max_level=max(LEVELS),
            help=LEVELS_HELPS[level],
        )
        return context

    def form_valid(self, form):
        ref = form.cleaned_data['source'].transcription
        txt = form.cleaned_data['transcription']
        self.diff = highlight_diffs(ref, txt)
        errors = get_diffs_per_normalizer(ref, txt)
        self.errors = [(name, diffs) for name, diffs in errors if diffs]
        return self.form_invalid(form)
