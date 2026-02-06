from django.db.models import Model, QuerySet
from django.http import Http404
from django.shortcuts import redirect
from rest_framework.request import Request
from wagtail.api.v2.utils import get_object_detail_url, parse_fields_parameter
from wagtail.api.v2.views import BaseAPIViewSet, PagesAPIViewSet
from wagtail.models import Page

import json
import urllib
from functools import cached_property
from typing import Type, Union

from accounts.models import HierarchicUser


class CustomPagesAPIViewSet(PagesAPIViewSet):
    meta_fields = [
        name for name in PagesAPIViewSet.meta_fields
        if name not in {'parent', 'alias_of', 'slug'}
    ] + ['teaser_thumbnail']
    detail_only_fields = []

    def serialize_sibling(self, sibling: Union[Page, None]):
        if sibling is None:
            return None
        return {'title': sibling.title, 'url': sibling.relative_url(None)}

    def find_view(self, request):
        # Copied from the original method, with extra HTTP headers added
        # to specify page metadata.

        queryset = self.get_queryset()

        try:
            obj = self.find_object(queryset, request)

            if obj is None:
                raise self.model.DoesNotExist

        except self.model.DoesNotExist:
            raise Http404("not found")

        # Generate redirect
        url = get_object_detail_url(
            self.request.wagtailapi_router, request, self.model, obj.pk
        )

        if url is None:
            # Shouldn't happen unless this endpoint isn't actually installed in the router
            raise Exception(
                "Cannot generate URL to detail view. Is '{}' installed in the API router?".format(
                    self.__class__.__name__
                )
            )

        response = redirect(url)
        obj: Page
        model = obj.content_type.model_class()
        response.headers['X-Page-Data'] = urllib.parse.quote(json.dumps({
            'id': obj.pk,
            'type': model._meta.label,
            'title': obj.title,
            'seo_title': obj.seo_title,
            'search_description': obj.search_description,
            'ancestors': [
                {
                    'id': ancestor.pk,
                    'title': ancestor.title,
                    'owner': self.serialize_instance('owner', ancestor.owner)
                } for ancestor in obj.get_ancestors().filter(depth__gt=1).select_related('owner')
            ],
            'previous': self.serialize_sibling(obj.get_prev_sibling()),
            'next': self.serialize_sibling(obj.get_next_sibling()),
            'url': obj.relative_url(None),
            'owner': self.serialize_instance('owner', obj.owner),
            'first_published_at': obj.first_published_at.isoformat(),
        }))
        return response

    @cached_property
    def parsed_fields(self):
        return parse_fields_parameter(
            self.request.GET.get('fields')
        ) + parse_fields_parameter(
            self.request.GET.get('extra_fields')
        )

    def get_related_serializer_class(self, name: str, model: Type[Model]):
        request = self.request
        fields_config = []
        for field, _, children in self.parsed_fields:
            if field == name and children:
                fields_config = children
                break

        cache_attr = '_cached_related_serializer_classes'
        cache_key = f'{model._meta.label}:{fields_config}'
        if not hasattr(request, cache_attr):
            setattr(request, cache_attr, {})
        request_cache = getattr(request, cache_attr)
        if cached_serializer_class := request_cache.get(cache_key):
            return cached_serializer_class

        router = request.wagtailapi_router
        endpoint_class = router.get_model_endpoint(model)
        endpoint_class = (
            endpoint_class[1] if endpoint_class else BaseAPIViewSet
        )
        serializer_class = endpoint_class._get_serializer_class(
            request.wagtailapi_router, model, fields_config=fields_config, nested=True,
        )

        request_cache[cache_key] = serializer_class
        return serializer_class

    def get_serializer_context(self):
        cache_attr = '_serializer_context'
        if cached := getattr(self.request, cache_attr, None):
            return cached
        context = super().get_serializer_context()
        setattr(self.request, cache_attr, context)
        return context

    def serialize_instance(self, name: str, instance: Model):
        serializer_class = self.get_related_serializer_class(name, type(instance))
        return serializer_class(instance, context=self.get_serializer_context()).data

    def serialize_queryset(self, name: str, queryset: QuerySet):
        serializer_class = self.get_related_serializer_class(name, queryset.model)
        return serializer_class(queryset, many=True, context=self.get_serializer_context()).data


class HierarchicUserViewSet(BaseAPIViewSet):
    model = HierarchicUser
    nested_default_fields = BaseAPIViewSet.nested_default_fields + ['username', 'first_name', 'last_name']
