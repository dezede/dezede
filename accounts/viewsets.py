import django_filters
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.filters import DateRangePickerWidget
from wagtail.admin.ui.tables import BooleanColumn, BulkActionsCheckboxColumn, Column
from wagtail.admin.widgets.boolean_radio_select import BooleanRadioSelect
from wagtail.users.views.users import IndexView, UserColumn, UserFilterSet, UserViewSet

from .forms import HierarchicUserCreationForm, HierarchicUserEditForm
from .models import HierarchicUser


class CustomIndexView(IndexView):
    @cached_property
    def columns(self):
        _UserColumn = self._get_title_column_class(UserColumn)
        return [
            BulkActionsCheckboxColumn("bulk_actions", obj_type="user"),
            _UserColumn(
                "name",
                accessor=str,
                label=_("Nom"),
                get_url=self.get_edit_url,
                classname="name",
            ),
            BooleanColumn(
                "is_staff",
                label=_("Statut équipe"),
                sort_key="is_staff" if "is_staff" in self.model_fields else None,
            ),
            Column(
                "mentor",
                accessor=lambda u: u.mentor,
                label=_("Responsable scientifique"),
                sort_key="mentor" if "mentor" in self.model_fields else None,
            ),
            BooleanColumn(
                "willing_to_be_mentor",
                label=_("Veut être responsable scientifique"),
                sort_key="willing_to_be_mentor"
                if "willing_to_be_mentor" in self.model_fields else None,
            ),
        ]


class CustomUserFilterSet(UserFilterSet):
    is_superuser = django_filters.BooleanFilter(
        label=_("Administrateur"),
        widget=BooleanRadioSelect,
    )
    last_login = django_filters.DateFromToRangeFilter(
        label=_("Dernière connexion"),
        widget=DateRangePickerWidget,
    )
    is_staff = django_filters.BooleanFilter(
        label=_("Statut équipe"),
        widget=BooleanRadioSelect,
    )
    willing_to_be_mentor = django_filters.BooleanFilter(
        label=_("Veut être responsable scientifique"),
        widget=BooleanRadioSelect,
    )
    mentor = django_filters.ModelChoiceFilter(
        queryset=HierarchicUser.objects.all(),
        label=_("Responsable scientifique"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "is_active" in self.filters:
            self.filters["is_active"].label = _("Actif")
        if "group" in self.filters:
            self.filters["group"].label = _("Groupe")

    class Meta(UserFilterSet.Meta):
        pass


class CustomUserViewSet(UserViewSet):
    index_view_class = CustomIndexView
    filterset_class = CustomUserFilterSet

    def get_form_class(self, for_update=False):
        if for_update:
            return HierarchicUserEditForm
        return HierarchicUserCreationForm
