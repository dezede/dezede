import json
import urllib
from django.http import Http404
from django.shortcuts import redirect
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.utils import get_object_detail_url
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.models import Page

from correspondence.api import LetterCorpusAPIViewSet
from libretto.api.rest.viewsets import *


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


wagtail_api_router = WagtailAPIRouter('wagtailapi')
wagtail_api_router.register_endpoint(r'pages', CustomPagesAPIViewSet)
wagtail_api_router.register_endpoint(r'correspondance', LetterCorpusAPIViewSet)
