from django.apps import AppConfig


class LibrettoConfig(AppConfig):
    name = 'libretto'

    def ready(self):
        # Register signals
        from . import signals

        from wagtail.models import ReferenceIndex
        from .models import (
            Auteur, ElementDeDistribution, ElementDeProgramme, ParenteDIndividus, ParenteDOeuvres,
            Membre, SourceEvenement, SourceOeuvre, SourceIndividu, SourceEnsemble, SourceLieu,
            SourcePartie,
        )
        for model in [
            Auteur, ElementDeDistribution, ElementDeProgramme, ParenteDIndividus, ParenteDOeuvres,
            Membre, SourceEvenement, SourceOeuvre, SourceIndividu, SourceEnsemble, SourceLieu,
            SourcePartie,
        ]:
            ReferenceIndex.register_model(model)
