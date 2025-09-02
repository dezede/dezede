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
from typing import Type


class CustomPagesAPIViewSet(PagesAPIViewSet):
    meta_fields = [
        name for name in PagesAPIViewSet.meta_fields
        if name not in {'parent', 'alias_of'}
    ]
    detail_only_fields = []

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
        model = obj.content_type.model_class() if isinstance(obj, Page) else type(model)
        response.headers['X-Page-Id'] = obj.pk
        response.headers['X-Page-Type'] = model._meta.label
        response.headers['X-Page-Title'] = urllib.parse.quote(obj.title if isinstance(obj, Page) else str(obj))
        response.headers['X-Page-Seo-Title'] = urllib.parse.quote(obj.seo_title if isinstance(obj, Page) else str(obj))
        response.headers['X-Page-Description'] = urllib.parse.quote(
                obj.search_description if isinstance(obj, Page) else ''
            )
        response.headers['X-Page-Ancestors'] = urllib.parse.quote(json.dumps([
                {'id': pk, 'title': title} for pk, title in obj.get_ancestors().filter(
                    depth__gt=1,
                ).values_list('pk', 'title')
            ] if isinstance(obj, Page) else []))
        response.headers['X-Page-Url'] = urllib.parse.quote(obj.relative_url(None) if isinstance(obj, Page) else '/')
        return response

    @cached_property
    def parsed_fields(self):
        return parse_fields_parameter(
            self.request.GET.get('fields')
        ) + parse_fields_parameter(
            self.request.GET.get('extra_fields')
        )

    def get_related_serializer_class(self, name: str, request: Request, model: Type[Model]):
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

    def serialize_instance(self, name: str, request: Request, instance: Model):
        serializer_class = self.get_related_serializer_class(name, request, type(instance))
        return serializer_class(instance, context=self.get_serializer_context()).data

    def serialize_queryset(self, name: str, request: Request, queryset: QuerySet):
        serializer_class = self.get_related_serializer_class(name, request, queryset.model)
        return serializer_class(queryset, many=True, context=self.get_serializer_context()).data
