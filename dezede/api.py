from rest_framework.routers import DefaultRouter
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import PagesAPIViewSet

from libretto.api.rest.viewsets import *


wagtail_api_router = WagtailAPIRouter('wagtailapi')
wagtail_api_router.register_endpoint(r'pages', PagesAPIViewSet)
