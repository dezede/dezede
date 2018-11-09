from django.conf.urls import url
from .views import TakeLevelView


urlpatterns = [
    url(r'^source$', TakeLevelView.as_view(), name='source_examen'),
]
