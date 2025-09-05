from rest_framework.fields import CharField
from wagtail.api.v2.serializers import StreamField as StreamFieldSerializer
from wagtail.rich_text import expand_db_html


class RichTextSerializer(CharField):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return expand_db_html(representation)
