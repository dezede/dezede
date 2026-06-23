from django.utils.translation import gettext_lazy as _
from wagtail.admin.admin_url_finder import AdminURLFinder
from wagtail.admin.panels import Panel


class ChildrenLinksPanel(Panel):
    class BoundPanel(Panel.BoundPanel):
        template_name = "libretto/panels/children_links.html"

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context)
            instance = self.instance
            children = []
            if instance is not None and instance.pk:
                # AdminURLFinder respects the user's permissions and returns
                # the Wagtail snippet edit URL (or None if not allowed).
                url_finder = AdminURLFinder(self.request.user)
                children = [
                    (url_finder.get_edit_url(child), child)
                    for child in instance.children.order_by("position")
                ]
            context["children"] = children
            return context
