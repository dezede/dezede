from rest_framework.routers import DefaultRouter
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import PagesAPIViewSet

from libretto.api.rest.viewsets import *


class CustomPagesAPIViewSet(PagesAPIViewSet):
    meta_fields = [
        name for name in PagesAPIViewSet.meta_fields
        if name not in {'parent', 'alias_of'}
    ]
    detail_only_fields = []


wagtail_api_router = WagtailAPIRouter('wagtailapi')
wagtail_api_router.register_endpoint(r'pages', CustomPagesAPIViewSet)
