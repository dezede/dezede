from django.utils.translation import gettext_lazy as _
from wagtail.admin.admin_url_finder import AdminURLFinder
from wagtail.admin.panels import InlinePanel, Panel


class ValidatedInlinePanel(InlinePanel):
    """
    Like ``InlinePanel`` but honours the child model's ``base_form_class``.

    Wagtail's ``InlinePanel`` builds the inline formset from the child's panels
    only (fields/widgets), defaulting the form to ``ClusterForm`` and ignoring
    any ``base_form_class`` declared on the child model. We inject it here so
    the child form's ``clean()`` validation (e.g. INCOMPATIBLES) is enforced
    when editing children inline.
    """
    def get_form_options(self):
        opts = super().get_form_options()
        base_form_class = getattr(
            self.db_field.related_model, 'base_form_class', None)
        if base_form_class is not None:
            opts['formsets'][self.relation_name]['form'] = base_form_class
        return opts


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
