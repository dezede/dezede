from django.urls import path
from .views import TakeLevelView


urlpatterns = [
    path('source', TakeLevelView.as_view(), name='source_examen'),
]
