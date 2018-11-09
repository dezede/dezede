from allauth.account.adapter import DefaultAccountAdapter
from django.utils.timezone import now

from examens.models import TakenExam


class HierarchicUserAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        data = form.cleaned_data
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.mentor = data['mentor']
        user.willing_to_be_mentor = data['willing_to_be_mentor']
        user.is_active = False
        user.last_login = now()

        user = super(HierarchicUserAdapter,
                     self).save_user(request, user, form, commit=commit)

        user.groups.add(*data['groups'])

        # This links the exam to that new user.
        exam = TakenExam.objects.get_for_request(request)
        exam.user = user
        exam.session = None
        exam.save()

        return user

    def confirm_email(self, request, email_address):
        super(HierarchicUserAdapter, self).confirm_email(request,
                                                         email_address)
        email_address.user.is_active = True
        email_address.user.save()
