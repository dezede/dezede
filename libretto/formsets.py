from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField
from modelcluster.forms import BaseChildFormSet


class TransientPkField(ModelChoiceField):
    def __init__(self, queryset, *args, valid_pks, **kwargs):
        super().__init__(queryset, *args, **kwargs)
        self.valid_pks = valid_pks

    def to_python(self, value):
        if value in self.empty_values:
            return None
        pk = self.queryset.model._meta.pk.to_python(value)
        # Only rows of this parent: a foreign id must not reach another row.
        if pk not in self.valid_pks():
            raise ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice', params={'value': value})
        return pk


def valid_pks(formset):
    if not hasattr(formset, '_valid_child_pks'):
        formset._valid_child_pks = {o.pk for o in formset.get_queryset()}
    return formset._valid_child_pks


def allow_deleted_children():
    """
    Let a child formset accept ids of rows that are gone from the database.

    modelcluster checks the hidden ``id`` of each child form against the
    database. Reverting to a revision brings back children deleted since, so
    the check made the whole form invalid, with no visible error. The ids are
    checked against the in-memory children of the parent instead, which are
    the revision's children on a revert.
    """
    if getattr(BaseChildFormSet, '_allows_deleted_children', False):
        return
    add_fields = BaseChildFormSet.add_fields

    def patched(self, form, index):
        add_fields(self, form, index)
        name = self.model._meta.pk.name
        field = form.fields.get(name)
        if type(field) is ModelChoiceField:
            form.fields[name] = TransientPkField(
                field.queryset, initial=field.initial,
                required=field.required, widget=field.widget,
                valid_pks=lambda: valid_pks(self))

    BaseChildFormSet.add_fields = patched
    BaseChildFormSet._allows_deleted_children = True
