from django.db.models import Avg
from django.utils.translation import gettext_lazy as _
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from dezede.views import CommonIndexView

from .forms import LevelAdminForm, TakenLevelForm
from .models import Level, TakenExam, TakenLevel

# The edit forms carry custom widgets and validation that Wagtail does not infer
# from the panels. Wiring them as ``base_form_class`` here (rather than on the
# models) avoids a models <-> forms circular import.
Level.base_form_class = LevelAdminForm
TakenLevel.base_form_class = TakenLevelForm


class LevelViewSet(SnippetViewSet):
    model = Level
    icon = 'list-ol'
    menu_label = _('niveaux')
    menu_name = 'levels'
    list_display = ('number',)
    add_to_admin_menu = False


class TakenExamViewSet(SnippetViewSet):
    model = TakenExam
    index_view_class = CommonIndexView
    icon = 'clipboard-list'
    # The annotated queryset (aggregates -> GROUP BY) reports ``ordered=False``,
    # so Wagtail would otherwise fall back to ``-pk``. Set the index's
    # ``default_ordering`` to the model's own ``Meta.ordering``.
    ordering = TakenExam._meta.ordering
    menu_label = _('examens passés')
    menu_name = 'taken-exams'
    add_to_admin_menu = False
    list_display = (
        'user', 'session', 'current_level', 'is_complete',
        'get_average_score', 'get_time_spent',
    )

    def get_queryset(self, request):
        return self.model._default_manager.annotate_time_spent().annotate(
            avg_score=Avg('taken_levels__score'))


@register_snippet
class ExamensViewSetGroup(SnippetViewSetGroup):
    menu_label = _('Examens')
    menu_icon = 'clipboard-list'
    add_to_admin_menu = True
    items = (LevelViewSet, TakenExamViewSet)
