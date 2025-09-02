from wagtail.api.v2.router import WagtailAPIRouter

from correspondence.viewsets import LetterCorpusAPIViewSet
from dezede.viewsets import CustomPagesAPIViewSet
from libretto.api.rest.viewsets import *


wagtail_api_router = WagtailAPIRouter('wagtailapi')
wagtail_api_router.register_endpoint(r'pages', CustomPagesAPIViewSet)
wagtail_api_router.register_endpoint(r'correspondance', LetterCorpusAPIViewSet)
