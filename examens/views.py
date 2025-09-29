from django.contrib import messages
from django.contrib.messages import SUCCESS
from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView

from .forms import TakenLevelForm
from .models import TakenExam, Level


SOURCE_LEVEL_SESSION_KEY = 'examen_source_level'


class TakeLevelView(UpdateView):
    form_class = TakenLevelForm
    template_name = 'examens/source.html'

    def get_object(self, queryset=None):
        self.last_taken_level = self.taken_exam.last_taken_level
        try:
            return self.taken_exam.take_level()
        except Level.DoesNotExist:
            raise Http404('No level yet.')

    def get_context_data(self, **kwargs):
        context = super(TakeLevelView, self).get_context_data(**kwargs)
        context.update(
            level=self.object.level,
            source=self.object.source,
            taken_exam=self.taken_exam,
            last_taken_level=self.last_taken_level,
            max_level_number=self.taken_exam.max_level_number,
        )
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.end = now()
        instance.save()
        if instance.passed:
            messages.add_message(
                self.request, SUCCESS,
                _('Félicitations ! La transcription était parfaite '
                  '<i class="fa fa-smile-o"></i>'))
        return redirect('source_examen')

    def check_for_completeness(self):
        self.taken_exam = TakenExam.objects.get_for_request(self.request)
        if self.taken_exam.is_complete():
            messages.add_message(
                self.request, SUCCESS,
                _('Excellent, vous avez fini toutes les étapes ! '
                  'Vous pouvez maintenant créer un compte utilisateur '
                  'si vous n’en possédez pas.'))
            return redirect('account_signup')

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        response = self.check_for_completeness()
        if response is not None:
            return response
        return super(TakeLevelView, self).get(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        response = self.check_for_completeness()
        if response is not None:
            return response
        return super(TakeLevelView, self).post(request, *args, **kwargs)
