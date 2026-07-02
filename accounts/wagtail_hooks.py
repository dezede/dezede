from wagtail import hooks
from wagtail.admin.viewsets.chooser import ChooserViewSet
from .models import HierarchicUser


class HierarchicUserChooserViewSet(ChooserViewSet):
    model = HierarchicUser


@hooks.register("register_admin_viewset")
def register_user_chooser_viewset():
    return HierarchicUserChooserViewSet("hierarchicuser_chooser")
