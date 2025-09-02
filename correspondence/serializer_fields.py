from rest_framework.fields import CharField
from wagtail.api.v2.serializers import StreamField as StreamFieldSerializer
from wagtail.rich_text import expand_db_html


class RichTextSerializer(CharField):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return expand_db_html(representation)


class ReferencesSerializer(StreamFieldSerializer):
    def to_representation(self, value):
        from dezede.viewsets import CustomPagesAPIViewSet

        viewset: CustomPagesAPIViewSet = self.context['view']
        return [
            viewset.serialize_instance(
                f'{self.field_name}__{reference.block_type}',
                self.context['request'],
                reference.value,
            )
            for reference in value
        ]
