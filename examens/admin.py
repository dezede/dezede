from django.contrib.admin import (
    TabularInline, StackedInline, register, ModelAdmin)
from django.db.models import Avg
from django.utils.translation import gettext_lazy as _

from .forms import LevelAdminForm, TakenLevelForm
from .models import Level, LevelSource, TakenExam, TakenLevel


class LevelSourceInline(TabularInline):
    model = LevelSource
    extra = 0


@register(Level)
class LevelAdmin(ModelAdmin):
    form = LevelAdminForm
    list_display = ('number',)
    inlines = (LevelSourceInline,)


class TakenLevelInline(StackedInline):
    model = TakenLevel
    form = TakenLevelForm
    readonly_fields = ('level', 'source', 'passed', 'get_score',
                       'start', 'end')
    fieldsets = (
        (None, {
            'fields': (
                ('level', 'source'), 'transcription', 'passed', 'get_score',
                ('start', 'end')),
        }),
    )
    extra = 0

    def get_score(self, obj):
        if obj.score is not None:
            return '%.1f / 20' % (obj.score * 20.0)
    get_score.short_description = _('note')


@register(TakenExam)
class TakenExamAdmin(ModelAdmin):
    list_display = ('user', 'session', 'get_current_level', 'is_complete',
                    'get_average_score', 'get_time_spent')
    inlines = (TakenLevelInline,)

    def get_queryset(self, request):
        qs = super(TakenExamAdmin, self).get_queryset(request)
        return qs.annotate_time_spent().annotate(
            avg_score=Avg('taken_levels__score'))

    def get_current_level(self, obj):
        return obj.current_level
    get_current_level.short_description = _('niveau actuel')

    def get_average_score(self, obj):
        if obj.avg_score is not None:
            return '%.1f / 20' % (obj.avg_score * 20.0)
    get_average_score.short_description = _('note moyenne')
    get_average_score.admin_order_field = 'avg_score'
