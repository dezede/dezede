from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.translation import gettext, gettext_lazy as _
from wagtail import hooks
from wagtail.admin.rich_text.converters.html_to_contentstate import BlockElementHandler
import wagtail.admin.rich_text.editors.draftail.features as draftail_features


@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">', static('dezede/admin.css'),
    )


@hooks.register('register_icons')
def register_icons(icons):
    return icons + [
        'wagtailfontawesomesvg/solid/align-center.svg',
        'wagtailfontawesomesvg/solid/align-right.svg',
    ]


@hooks.register('register_rich_text_features')
def register_align_features(features):
    for align, description in [
        ('center', gettext('Centrer')),
        ('right', gettext('Aligner à droite')),
    ]:
        feature_name = f'align-{align}'
        type_ = feature_name
        element = feature_name

        control = {
            'type': type_,
            'icon': feature_name,
            'description': description,
            'element': element,
        }

        features.register_editor_plugin(
            'draftail', feature_name, draftail_features.BlockFeature(control)
        )

        features.register_converter_rule('contentstate', feature_name, {
            'from_database_format': {element: BlockElementHandler(type_)},
            'to_database_format': {'block_map': {type_: {'element': element, 'props': {}}}},
        })
